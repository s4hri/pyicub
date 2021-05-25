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
from pyicub.iCubHelper import iCub, ROBOT_TYPE, ICUB_PARTS

yarp.Network.init()

icub = iCub(ROBOT_TYPE.ICUB_SIMULATOR, logtype="DEBUG")
rightarm_ctrl = icub.getPositionController(ICUB_PARTS.RIGHT_ARM)
torso_ctrl = icub.getPositionController(ICUB_PARTS.TORSO)

icub.gaze.setTrackingMode(True)
icub.gaze.lookAt3DPoint(-0.2, 0.2, 1.0)
torso_ctrl.move(target_joints=[5.0, -4.0, -2.0], req_time=1.0)
rightarm_ctrl.move(target_joints=[10.06, 99.47, 5.31, 102.67, -13.50, -4.21], req_time=1.0, joints_list=[0, 1, 2, 3, 4, 5], waitMotionDone=True)
rightarm_ctrl.move(target_joints=[9.97, 99.63, 6.34, 97.23, -10.95, -3.11], req_time=1.0, joints_list=[0, 1, 2, 3, 4, 5], waitMotionDone=True)
rightarm_ctrl.move(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], req_time=1.0, joints_list=[0, 1, 2, 3, 4, 5], waitMotionDone=True)
