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
        self.__rpc__ = RpcClient("/faceLandmarks/rpc:i")
        self.__port_landmarks__ = BufferedReadPort("/faceLandmarksPyCtrl/landmarks:i", "/faceLandmarks/landmarks:o")

    def sendCmd(self, cmd, option):
        btl = yarp.Bottle()
        btl.clear()
        map(btl.addString, [cmd, option])
        return self.__rpc__.execute(btl)

    def getLandmark(self, index, shouldWait=False):
        L = self.getLandmarks(shouldWait)
        if L is None:
            return (None, None)
        return map(int, L[index].split())

    def getCenterFace(self, shouldWait=False):
        res = self.getLandmark(27, shouldWait)
        if type(res) == map:
            (fx, fy) = res
            return [fx, fy]
        else:
            return (None, None)

    def getLandmarks(self, shouldWait=False):
        btl = self.__port_landmarks__.read(shouldWait)
        if btl is None:
            return None
        return btl.toString()[2:-2].split(') (')

    def close(self):
        self.__rpc__.close()
