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
from pyicub.api.yarp_classes.Rpc import RpcClient

class speechPyCtrl:

    def __init__(self):
        self.__rpc__ = RpcClient("/icub/speech:rpc")

    def __sayCmd__(self, something):
        cmd = yarp.Bottle()
        cmd.clear()
        map(cmd.addString, ["say", something])
        return self.__rpc__.execute(cmd)

    def say(self, something):
        self.__sayCmd__(something)

    def setPitch(self, pitch):
        cmd = yarp.Bottle()
        cmd.clear()
        map(cmd.addString, ["setPitch"])
        map(cmd.addInt, [pitch])
        return self.__rpc__.execute(cmd)

    def setSpeed(self, speed):
        cmd = yarp.Bottle()
        cmd.clear()
        map(cmd.addString, ["setSpeed"])
        map(cmd.addInt, [speed])
        return self.__rpc__.execute(cmd)

    def close(self):
        self.__rpc__.close()
