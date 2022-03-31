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
        self._future_ = None
        self._logger_ = YarpLogger.getLogger()
        
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

    @staticmethod
    def join(requests):
        for req in requests:
            req.wait_for_completed()
    
    def __str__(self):
        return str(self.info())

    def run(self, *args, **kwargs):
        self._future_ = self._executor_.submit(self._target_, *args, **kwargs)
        self._status_ = iCubRequest.RUNNING
        self._logger_.debug("iCubRequest %s STARTED!" % self.req_id)
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
            self._logger_.debug("iCubRequest %s COMPLETED! %s" % (self.req_id, self.info()))
        elif self._status_ == iCubRequest.TIMEOUT:
            self._logger_.warning("iCubRequest %s TIMEOUT! %s" % (self.req_id, self.info()))
        elif self._status_ == iCubRequest.FAILED:
            self._logger_.error("iCubRequest %s ERROR! %s" % (self.req_id, self.info()))
        
        self._retval_ = res
        return res

    def wait_for_completed(self):
        self._executor_.shutdown(wait=True)
        return self._retval_

    def info(self):
        info = {}
        info['target'] = self.target.__name__
        info['req_id'] = self.req_id
        info['status'] = self.status
        info['start_time'] = self.start_time
        info['end_time'] = self.end_time
        info['duration'] = self.duration
        info['exception'] = self.exception
        info['retval'] = self.retval
        return info

class iCubRequestsManager(metaclass=SingletonMeta):

    CSV_COLUMNS = ['req_id','target','status', 'start_time', 'end_time', 'duration', 'exception', 'retval']

    def __init__(self):
        self._pending_requests_ = {}
        self._completed_requests_ = {}
        self._req_topics_ = {}
        self._lock = threading.Lock()

    @property
    def pending_requests(self):
        return self._pending_requests_

    @property
    def completed_requests(self):
        return self._completed_requests_

    def create(self, timeout, target, name=''):
        with self._lock:
            if not name in self._req_topics_.keys():
                self._req_topics_[name] = 0
            else:
                self._req_topics_[name] += 1
            req_id = name + '/' + str(self._req_topics_[name])
            req = iCubRequest(req_id, timeout, target)
            self._pending_requests_[req_id] = req
        return req

    def join(self, csv_output_filename=None):
        while True:
            if len(self._pending_requests_.values()) > 0:
                request = list(self._pending_requests_.values())[0]
                request.wait_for_completed()
                with self._lock:
                    self._completed_requests_[request.req_id] = request
                    del self._pending_requests_[request.req_id]
            else:
                break
        if not csv_output_filename is None:
            self.save_requests(filename=csv_output_filename)
        self.flush_requests()

    def flush_requests(self):
        del self._completed_requests_
        self._completed_requests_ = {}


    def run(self, req_id, *args, **kwargs):
        self._pending_requests_[req_id].run(*args, **kwargs)
        return self._pending_requests_[req_id].info()
    
    def save_requests(self, filename, mode='w'):
        with open(filename, mode, encoding='UTF-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=iCubRequestsManager.CSV_COLUMNS)
            writer.writeheader()
            for req in self._completed_requests_.values():
                writer.writerow(req.info())
