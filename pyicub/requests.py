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
from pyicub.utils import SingletonMeta
from pyicub.core.logger import YarpLogger

class iCubRequest:

    INIT    = 'INIT'
    RUNNING = 'RUNNING'
    TIMEOUT = 'TIMEOUT'
    DONE    = 'DONE'
    FAILED  = 'FAILED'

    TIMEOUT_REQUEST = 60.0

    def __init__(self, req_id, timeout, target):
        self._start_time_ = round(time.perf_counter(), 4)
        self._end_time_ = None
        self._req_id_ = req_id
        self._status_ = iCubRequest.INIT
        self._timeout_ = timeout
        self._duration_ = None
        self._exception_ = None
        self._executor_ = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._target_ = target
        self._retval_ = None
        self._logger_ = YarpLogger.getLogger()

    @staticmethod
    def join(requests):
        for req in requests:
            req.wait_for_completed()

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
    def target(self):
        return self._target_

    def run(self, *args, **kwargs):
        self._future_ = self._executor_.submit(self._target_, *args, **kwargs)
        self._status_ = iCubRequest.RUNNING
        self._logger_.debug("iCubRequest <%d> STARTED!" % self.req_id)
        self._future_.add_done_callback(self.on_completed)

    def on_completed(self, future):
        res = None
        try:
            res = future.result(self._timeout_)
            self._status_ = iCubRequest.DONE
        except concurrent.futures.TimeoutError as e:
            self._exception_ = str(e)
            self._status_ = iCubRequest.TIMEOUT
        except Exception as e:
            self._exception_ = str(e)
            self._status_ = iCubRequest.FAILED
            raise(e)
        finally:
            self._end_time_ = round(time.perf_counter(), 4)
            self._duration_ = round(self._end_time_ - self._start_time_, 4)
            self._executor_.shutdown(wait=False)
        if self._status_ == iCubRequest.DONE:
            self._logger_.debug("iCubRequest <%d> COMPLETED! %s" % (self.req_id, self.info()))
        elif self._status_ == iCubRequest.TIMEOUT:
            self._logger_.warning("iCubRequest <%d> TIMEOUT! %s" % (self.req_id, self.info()))
        elif self._status_ == iCubRequest.FAILED:
            self._logger_.error("iCubRequest <%d> ERROR! %s" % (self.req_id, self.info()))
        self._retval_ = res
        return res


    def wait_for_completed(self):
        self._executor_.shutdown(wait=True)
        return self._retval_

    def info(self):
        info = {}
        info['target'] = self.target.__name__
        info['id'] = self.req_id
        info['status'] = self.status
        info['start_time'] = self.start_time
        info['end_time'] = self.end_time
        info['duration'] = self.duration
        info['exception'] = self.exception
        info['retval'] = self.retval
        return info

class iCubRequestsManager(metaclass=SingletonMeta):

    def __init__(self):
        self._requests_ = {}
        self._lock = threading.Lock()

    def create(self, timeout, target):
        with self._lock:
            if len(self._requests_) == 0:
                req_id = 0
            else:
                req_id = max(self._requests_.keys()) + 1
            req = iCubRequest(req_id, timeout, target)
            self._requests_[req_id] = req
        return req

    def flush_requests(self):
        del self._requests_
        self._requests_ = {}


    def run(self, req_id, *args, **kwargs):
        self._requests_[req_id].run(*args, **kwargs)
        return self._requests_[req_id].info()
