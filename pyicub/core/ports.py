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
from pyicub.core.logger import YarpLogger


class CustomCallback(yarp.BottleCallback):
    def __init__(self, user_callback):
        yarp.BottleCallback.__init__(self)
        self.__user_callback__ = user_callback

    def onRead(self, bottle):
        self.__user_callback__(bottle)

class BufferedPort:

    def __init__(self):
        self.__logger__ = YarpLogger.getLogger()
        self.__port__ = yarp.BufferedPortBottle()
        self.__port_name__ = ''

    @property
    def name(self):
        return self.__port_name__

    def open(self, port):
        self.__logger__.debug("Opening BufferedPort: %s" % port)
        res = self.__port__.open(port)
        if res is True:
            self.__port_name__ = port
        self.__logger__.debug("BufferedPort: %s open! res:%s" % (port, str(res)))

    def read(self, shouldWait=True):
        self.__logger__.debug("Reading from %s, shouldWait:%s STARTED!" % (self.__port_name__, str(shouldWait)))
        res = self.__port__.read(shouldWait)
        self.__logger__.debug("Reading from %s, value:%s COMPLETED!" % (self.__port_name__, str(res)))
        return res

    def lastRead(self):
        self.__logger__.debug("LastRead from %s STARTED!" % self.__port_name__)
        res = self.__port__.lastRead()
        self.__logger__.debug("LastRead from %s, res:%s COMPLETED!" % (self.__port_name__, str(res)))

    def write(self, msg, forceStrict=False):
        self.__logger__.debug("Writing to %s, msg:%s forceStrict=%s STARTED!" % (self.__port_name__, str(msg), str(forceStrict)))
        btl = self.__port__.prepare()
        btl.fromString(msg)
        res = self.__port__.write(forceStrict)
        self.__logger__.debug("Writing to %s, res=%s COMPLETED!" % (self.__port_name__, str(res)))

    def setStrict(self):
        self.__port__.setStrict()

    def prepare(self):
        btl = self.__port__.prepare()
        btl.clear()
        return btl

class BufferedReadPort(BufferedPort):

    def __init__(self, port_name, port_src, callback=None):
        BufferedPort.__init__(self)
        self.__port_name__ = port_name
        self.__port_src__ = port_src
        if callback:
            self.__callback__ = CustomCallback(callback)
            self.__port__.useCallback(self.__callback__)
        self.open(self.__port_name__)
        yarp.Network.connect(self.__port_src__, self.__port_name__)


class BufferedWritePort(BufferedPort):

    def __init__(self, port_name, port_dst):
        BufferedPort.__init__(self)
        self.__port_name__ = port_name
        self.__port_dst__ = port_dst
        self.__port__.open(self.__port_name__)
        yarp.Network.connect(self.__port_name__, self.__port_dst__)
