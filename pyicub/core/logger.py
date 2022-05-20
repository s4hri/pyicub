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

import yarp
import logging
import datetime
import os


class _Logger:

    _instance = None

    def __init__(self):
        if _Logger._instance != None:
            raise Exception("This class is a singleton!")
        else:
            _Logger._instance = self

        self._logging = True
        self._logger = None

    def disable_logs(self):
        self._logging = False

    def enable_logs(self):
        self._logging = True

    def error(self, msg):
        if self._logging:
            self._logger.error(msg)

    def warning(self, msg):
        if self._logging:
            self._logger.warning(msg)

    def debug(self, msg):
        if self._logging:
            self._logger.debug(msg)

    def info(self, msg):
        if self._logging:
            self._logger.info(msg)


class YarpLogger(_Logger):

    @staticmethod
    def getLogger():
        if YarpLogger._instance == None:
            YarpLogger()
        return YarpLogger._instance

    def __init__(self):
        _Logger.__init__(self)
        self._yarp_logger = yarp.Log("",0,"") #FIXME: without params I get segfault
        self._logger = self._yarp_logger

class PyicubLogger(_Logger):

    @staticmethod
    def getLogger():
        if PyicubLogger._instance == None:
            PyicubLogger()
        return PyicubLogger._instance

    FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    FORMAT_VERBOSE = '%(asctime)s - %(levelname)s - %(module)s - %(process)d - %(thread)d - %(message)s'
    FORMAT_JSON = '{"asctime": "%(asctime)-15s", "created": %(created)f, "relativeCreated": %(relativeCreated)f, "levelname": "%(levelname)s", "module": "%(module)s", "process": %(process)d, "processName": "%(processName)s", "thread": %(thread)d, "threadName": "%(threadName)s", "message": "%(message)s"}'
    LOGGING_LEVEL = logging.DEBUG

    def __init__(self):
        _Logger.__init__(self)

    def configure(self, logging_level, logging_format, logging_file=False, logging_path='.'):
        self._logging_level = logging_level
        self._logging_path = logging_path
        self._logging_format = logging_format
        self._logger = logging.getLogger('pyicub')
        self._logger.setLevel(logging_level)
        self.addStreamHandler()
        if logging_file is True:
            self.addFileHandler(logging_path)

    def addFileHandler(self, path):
        datetimestr = datetime.datetime.now().strftime('%d.%m.%Y_%H:%M')
        main_name = 'pyicub'
        filename = "%s_%s.log" % (main_name, datetimestr)
        filepath = os.path.join(path, filename)
        ch = logging.FileHandler(filepath, mode='w')
        ch.setLevel(self._logging_level)
        formatter = logging.Formatter(self._logging_format)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def addStreamHandler(self, stream=None):
        ch = logging.StreamHandler(stream) # None defaults to sys.stderr
        ch.setLevel(self._logging_level)
        formatter = logging.Formatter(self._logging_format)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

