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
from pyicub.core.Rpc import RpcClient
from pyicub.core.BufferedPort import BufferedReadPort

class faceLandmarksPyCtrl:

    def __init__(self):
        self.__landmarks__ = None
        self.__port_landmarks__ = BufferedReadPort("/faceLandmarksPyCtrl/landmarks:i", "/faceLandmarks/landmarks:o", callback=self.onRead)

    def onRead(self, bottle):
        if bottle is None:
            self.__landmarks__ = None
        else:
            self.__landmarks__ = bottle.toString()[2:-2].split(') (')

    def sendCmd(self, cmd, option):
        btl = yarp.Bottle()
        btl.clear()
        map(btl.addString, [cmd, option])
        return self.__rpc__.execute(btl)

    def getLandmark(self, index):
        if self.__landmarks__ is None:
            return (None, None)
        return map(int, self.__landmarks__[index].split())

    def getCenterEyes(self):
        res = self.getLandmark(27)
        if type(res) == map:
            (fx, fy) = res
            return [fx, fy]
        else:
            return (None, None)
