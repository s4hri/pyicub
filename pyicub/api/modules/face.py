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
from pyicub.api.classes.BufferedPort import BufferedWritePort

class facePyCtrl:

    def __init__(self, robot):
        self.__faceraw_port__ = BufferedWritePort('/face/raw/out', '/%s/face/raw/in' % robot)

    def sendRaw(self, cmd):
        self.__faceraw_port__.write(cmd)
