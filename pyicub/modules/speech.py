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

from multiprocessing.connection import wait
import yarp
from pyicub.core.ports import BufferedWritePort
from pyicub.core.rpc import RpcClient

class speechPyCtrl:

    def __init__(self, robot):
         self.__port__ = BufferedWritePort("/pyicub/speech:o", "/%s/speech:rpc" % robot)

    def say(self, something):
        self.__port__.write("say \"%s\"" % something)

    def setPitch(self, pitch):
        self.__port__.write("setPitch %d" % pitch)

    def setSpeed(self, speed):
        self.__port__.write("setSpeed %d" % speed)

    def close(self):
        self.__port__.close()

class iSpeakPyCtrl:

    def __init__(self):
         self.__port__ = BufferedWritePort("/pyicub/speech:o", "/iSpeak")
         self.__rpcPort__ = RpcClient("/iSpeak/rpc")

    def say(self, something, waitActionDone=True):
        self.__port__.write("\"%s\"" % something)
        btl = yarp.Bottle()
        btl.clear()
        btl.addString("stat")
        res = self.__rpcPort__.execute(btl)
        if waitActionDone:
            while res.toString() == "speaking":
                res = self.__rpcPort__.execute(btl)
                yarp.delay(0.01)
        return res

    def close(self):
        self.__port__.close()
