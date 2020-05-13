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
from pyicub.api.classes.Rpc import RpcClient


class emotionsPyCtrl:

    def __init__(self, robot):
        self.__rpc__ = RpcClient("/%s/face/emotions/in" % robot)

    def __emoCmd__(self, part, emo):
        cmd = yarp.Bottle()
        cmd.clear()
        cmd.addString("set")
        cmd.addString(part)
        cmd.addString(emo)
        return self.__rpc__.execute(cmd)

    def smile(self):
        self.__emoCmd__("all", "hap")

    def eb_smile(self):
        self.__emoCmd__("leb", "hap")
        self.__emoCmd__("reb", "hap")

    def eb_surprised(self):
        self.__emoCmd__("leb", "sur")
        self.__emoCmd__("reb", "sur")

    def surprised(self):
        self.__emoCmd__("mou", "sur")
        self.__emoCmd__("leb", "sur")
        self.__emoCmd__("reb", "sur")

    def neutral(self):
        self.__emoCmd__("mou", "neu")
        self.__emoCmd__("leb", "neu")
        self.__emoCmd__("reb", "neu")

    def sad(self):
        self.__emoCmd__("mou", "sad")
        self.__emoCmd__("leb", "sad")
        self.__emoCmd__("reb", "sad")

    def openingEyes(self):
        self.__emoCmd__("eli", "hap")

    def closingEyes(self):
        self.__emoCmd__("eli", "sad")

    def cun(self):
        self.__emoCmd__("leb", "cun")
        self.__emoCmd__("reb", "cun")

    def angry(self):
        self.__emoCmd__("all", "ang")

    def evil(self):
        self.__emoCmd__("all", "evil")

    def sendCmd(self, part, emo):
        return self.__emoCmd__(part, emo)

    def close(self):
        self.__rpc__.close()
