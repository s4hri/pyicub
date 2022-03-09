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

import yarp
from pyicub.core.logger import YarpLogger


class CustomCallback(yarp.BottleCallback):
    def __init__(self, user_callback):
        yarp.BottleCallback.__init__(self)
        self.__user_callback__ = user_callback

    def onRead(self, bottle, reader):
        self.__user_callback__(bottle)

class BufferedPort:

    def __init__(self):
        self.__logger__ = YarpLogger.getLogger()
        self.__port__ = yarp.BufferedPortBottle()

    @property
    def name(self):
        return self.__portname__

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
