# BSD 2-Clause License
#
# Copyright (c) 2022, Social Cognition in Human-Robot Interaction,
#                     Istituto Italiano di Tecnologia, Genova
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import time
import concurrent.futures
import threading
import csv
import ctypes
import os

from pyicub.utils import SingletonMeta

import atexit
from concurrent.futures import thread as thf
atexit.unregister(thf._python_exit)


class iCubRequest:

    INIT    = 'INIT'
    RUNNING = 'RUNNING'
    TIMEOUT = 'TIMEOUT'
    DONE    = 'DONE'
    FAILED  = 'FAILED'

    TIMEOUT_REQUEST = 60.0

    def __init__(self, req_id, timeout, target, logger, ts_ref=0.0, tag=''):
        self._ts_ref_ = ts_ref
        self._logger_ = logger
        self._creation_time_ = round(time.perf_counter() - self._ts_ref_, 4)
        self._start_time_ = None
        self._end_time_ = None
        self._req_id_ = req_id
        self._tag_ = tag
        self._status_ = iCubRequest.INIT
        self._timeout_ = timeout
        self._duration_ = None
        self._exception_ = None
        self._target_executor_ = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._req_executor_ = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._target_ = target
        self._retval_ = None
        self._future_target_ = None
        self._future_req_ = None

    @property
    def creation_time(self):
        return self._creation_time_

    @property
    def duration(self):
        return self._duration_

    @property
    def end_time(self):
        return self._end_time_

    @property
    def exception(self):
        return self._exception_

    @property
    def future_target(self):
        return self._future_target_

    @property
    def future_req(self):
        return self._future_req_

    @property
    def req_id(self):
        return self._req_id_

    @property
    def retval(self):
        return self._retval_

    @property
    def status(self):
        return self._status_

    @property
    def start_time(self):
        return self._start_time_

    @property
    def tag(self):
        return self._tag_

    @property
    def target(self):
        return self._target_

    def __str__(self):
        return str(self.info())

    def run(self, *args, **kwargs):
        self._future_target_ = self._target_executor_.submit(self._target_, *args, **kwargs)
        self._logger_.debug("iCubRequest tag=%s, req_id=%s STARTED!" % (self.tag, self.req_id))
        self._status_ = iCubRequest.RUNNING
        self._start_time_ = round(time.perf_counter() - self._ts_ref_, 4)
        self._future_req_ = self._req_executor_.submit(self._execute_)

    def _stop_request_(self):
        self._target_executor_.shutdown(wait=False)
        for t in self._target_executor_._threads:
            self._terminate_thread_(t)

    def cancel(self):
        self._logger_.debug("iCubRequest tag=%s, req_id=%s cancelling target future ..." % (self.tag, self.req_id) )
        self._future_target_.cancel()
        self._stop_request_()
        self._target_executor_.shutdown(wait=False)

    def _terminate_thread_(self, thread):
        if not thread.isAlive():
           return
        exc = ctypes.py_object(SystemError)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), exc)
        if res == 0:
            raise ValueError("nonexistent thread id")
        elif res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
        self._logger_.debug("Thread %d stopped!" % thread.native_id)

    def _execute_(self):
        res = None
        try:
            res = self._future_target_.result(self._timeout_)
            self._status_ = iCubRequest.DONE
        except concurrent.futures.TimeoutError as e:
            self._exception_ = repr(e)
            self._status_ = iCubRequest.TIMEOUT
        except Exception as e:
            self._exception_ = repr(e)
            self._status_ = iCubRequest.FAILED
            raise(e)
        finally:
            self._end_time_ = round(time.perf_counter() - self._ts_ref_, 4)
            self._duration_ = round(self._end_time_ - self._start_time_, 4)
            if self._status_ == iCubRequest.DONE:
                self._logger_.debug("iCubRequest tag=%s, req_id=%s COMPLETED! %s" % (self.tag, self.req_id, self.info()))
            elif self._status_ == iCubRequest.TIMEOUT:
                self._logger_.warning("iCubRequest tag=%s, req_id=%s TIMEOUT! %s" % (self.tag, self.req_id, self.info()))
                self.cancel()
            elif self._status_ == iCubRequest.FAILED:
                self._logger_.error("iCubRequest tag=%s, req_id=%s ERROR! %s" % (self.tag, self.req_id, self.info()))
            self._retval_ = res
            return self

    def wait_for_completed(self):
        self._req_executor_.shutdown(wait=True)

    def info(self):
        info = {}
        info['target'] = self.target.__name__
        info['req_id'] = self.req_id
        info['tag'] = self.tag
        info['status'] = self.status
        info['creation_time'] = self.creation_time
        info['start_time'] = self.start_time
        info['end_time'] = self.end_time
        info['duration'] = self.duration
        info['exception'] = self.exception
        info['retval'] = self.retval
        return info

class iCubRequestsManager(metaclass=SingletonMeta):

    CSV_COLUMNS = ['req_id', 'target', 'tag', 'status', 'creation_time', 'start_time', 'end_time', 'duration', 'exception', 'retval']

    def __init__(self, logger, logging=False, logging_path=None):
        self._pending_futures_ = {}
        self._req_topics_ = {}
        self._last_req_id_ = 0
        self._lock = threading.Lock()
        self._logger_ = logger
        self._logging_ = logging
        self._logging_path_ = logging_path
        if self._logging_ and self._logging_path_:
            self._logfile_ = os.path.join(self._logging_path_, "pyicub_requests.csv")
            with open(self._logfile_, mode='w', encoding='UTF-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=iCubRequestsManager.CSV_COLUMNS)
                writer.writeheader()
        else:
            self._logging_ = False


    @property
    def pending_futures(self):
        return self._pending_futures_
    
    @property
    def logger(self):
        return self._logger_

    def create(self, timeout, target, name='', ts_ref=0.0, prefix=''):
        with self._lock:
            if not name in self._req_topics_.keys():
                self._req_topics_[name] = 1
            else:
                self._req_topics_[name] += 1
            self._last_req_id_ += 1
            req_id = str(self._last_req_id_)
            tag = name + '/' + str(self._req_topics_[name])
            if prefix:
                req_id = prefix + '/' + req_id
            req = iCubRequest(req_id, timeout, target, self._logger_, ts_ref, tag)
            if self._logging_:
                self._log_request_(req)
        return req

    
    def join_requests(self, requests):
        for req in requests:
            req.wait_for_completed()
    
    def join_pending_requests(self, timeout=iCubRequest.TIMEOUT_REQUEST):
        while self.pending_futures.values():
            current_pending_reqs = self.pending_futures.values()
            concurrent.futures.wait(current_pending_reqs, timeout=timeout, return_when=concurrent.futures.ALL_COMPLETED)

    def run_request(self, req, wait_for_completed, *args, **kwargs):
        req.run(*args, **kwargs)
        if self._logging_:
            self._log_request_(req)
        self._pending_futures_[req.req_id] = req.future_req
        req.future_req.add_done_callback(self._finalize_)
        if wait_for_completed:
            req.wait_for_completed()

    def _finalize_(self, future):
        req = future.result()
        if self._logging_:
            self._log_request_(future.result())
        del self._pending_futures_[req.req_id]

    def _log_request_(self, req):
            with open(self._logfile_, 'a', encoding='UTF-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=iCubRequestsManager.CSV_COLUMNS)
                writer.writerow(req.info())
            
