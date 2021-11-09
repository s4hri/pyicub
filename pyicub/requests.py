#   Copyright (C) 2021  Davide De Tommaso
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>


from pyicub.utils import SingletonMeta

import time
import concurrent.futures

class iCubRequest:

    INIT    = 'INIT'
    RUNNING = 'RUNNING'
    TIMEOUT = 'TIMEOUT'
    DONE    = 'DONE'
    FAILED  = 'FAILED'

    TIMEOUT_REQUEST = 30.0

    def __init__(self, req_id, timeout, target):
        self._start_time_ = time.perf_counter()
        self._end_time_ = None
        self._req_id_ = req_id
        self._status_ = iCubRequest.INIT
        self._timeout_ = timeout
        self._duration_ = None
        self._exception_ = None
        self._executor_ = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._target_ = target
        self._retval_ = None

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
        self._future_.add_done_callback(self.on_completed)

    def on_completed(self, future):
        self._end_time_ = time.perf_counter()
        self._duration_ = self._end_time_ - self._start_time_
        self._status_ = iCubRequest.DONE

    def wait_for_completed(self):
        res = None
        try:
            res = self._future_.result(self._timeout_)
        except Exception as e:
            self._end_time_ = time.perf_counter()
            self._duration_ = self._end_time_ - self._start_time_
            self._status_ = iCubRequest.FAILED
            self._exception_ = str(e)
            raise(e)
        finally:
            self._executor_.shutdown(wait=False)
        self._retval_ = res
        return res

class iCubRequestsManager(metaclass=SingletonMeta):

    def __init__(self):
        self._requests_ = {}

    def create(self, timeout, target):
        if len(self._requests_) == 0:
            req_id = 0
        else:
            req_id = max(self._requests_.keys()) + 1
        req = iCubRequest(req_id, timeout, target)
        self._requests_[req_id] = req
        return req

    def run(self, req_id, *args, **kwargs):
        self._requests_[req_id].run(*args, **kwargs)
        threading.Thread(target=self._requests_[req_id].wait_for_completed).start()
        return self.info(req_id)

    def info(self, req_id):
        info = {}
        req_id = int(req_id)
        info['target'] = self._requests_[req_id].target.__name__
        info['id'] = self._requests_[req_id].req_id
        info['status'] = self._requests_[req_id].status
        info['start_time'] = self._requests_[req_id].start_time
        info['end_time'] = self._requests_[req_id].end_time
        info['duration'] = self._requests_[req_id].duration
        info['exception'] = self._requests_[req_id].exception
        info['retval'] = self._requests_[req_id].retval
        return info
