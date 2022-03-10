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

class YarpLogger:

    _instance = None

    @staticmethod
    def getLogger():
        if YarpLogger._instance == None:
            YarpLogger()
        return YarpLogger._instance

    def __init__(self):
        if YarpLogger._instance != None:
            raise Exception("This class is a singleton!")
        else:
            YarpLogger._instance = self
        self.__yarp_logger__ = yarp.Log("",0,"") #FIXME: without params I get segfault
        self.enable_logs()

    def disable_logs(self):
        self.__logging__ = False

    def enable_logs(self):
        self.__logging__ = True

    def error(self, msg):
        if self.__logging__:
            self.__yarp_logger__.error(msg)

    def warning(self, msg):
        if self.__logging__:
            self.__yarp_logger__.warning(msg)

    def debug(self, msg):
        if self.__logging__:
            self.__yarp_logger__.debug(msg)

    def info(self, msg):
        if self.__logging__:
            self.__yarp_logger__.info(msg)
