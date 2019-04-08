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
import time

from pyicub.api.iCubHelper import iCub, ROBOT_TYPE, ICUB_PARTS

yarp.Network.init()

icub = iCub(ROBOT_TYPE.ICUB)
head_ctrl = icub.getPositionController(ICUB_PARTS.HEAD)
head_ctrl.move(target_joints=[-15.0, 0.0, 0.0, 0.0, 0.0, 5.0], req_time=1.0)
