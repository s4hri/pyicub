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
import time as tt

class PositionController:

    def __init__(self, yarp_driver, joints_list):
        self.__IControlMode__ = yarp_driver.viewIControlMode()
        for joint in joints_list:
            self.__IControlMode__.setControlMode(joint, yarp.VOCAB_CM_POSITION)
        self.__IPositionControl__ = yarp_driver.viewIPositionControl()

    def getIPositionControl(self):
        return self.__IPositionControl__

    def getIEncoders(self):
        return self.__IEncoders__
