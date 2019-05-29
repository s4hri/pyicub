#   Copyright (C) 2019  Davide De Tommaso
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

import yarp
import threading
import time

from pyicub.api.classes.Logger import YarpLogger

class GenericController(object):

    TIMEOUT_LOCK = 5.0

    def __init__(self, logger):
        self.__Lock__ = threading.Lock()
        self.__logger__ = logger

    def __atomicDecorator__(foo):
        def f(self, *args, **kwargs):
            t0 = time.time()
            #res = self.__Lock__.acquire(timeout=GenericController.TIMEOUT_LOCK) # not compatible with Python vers < 3.2
            res = self.__Lock__.acquire()
            if res is False:
                err = "%s:%s(%s) Failed to acquire the Lock, the resource is busy, not available or timeout occurred!" % (type(self).__name__, foo.__name__, args[0:])
                self.__logger__.error(err)
                return False
            foo(self, *args, **kwargs)
            if kwargs:
                args = str(kwargs)
            else:
                args = str(args[0:])
            self.__Lock__.release()
            elapsed_time_ms = (time.time() - t0)*1000
            self.__logger__.debug("%s:%s(%s) has been executed successful in %d ms" % (type(self).__name__, foo.__name__, args, elapsed_time_ms))
            time.sleep(0.001)
            return elapsed_time_ms
        return f

    def __waitMotionDone__(self, timeout):
        raise NotImplementedError("method needs to be defined by sub-class")

    __atomicDecorator__ = staticmethod( __atomicDecorator__ )
