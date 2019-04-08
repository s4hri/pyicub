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

icub = iCub(ROBOT_TYPE.ICUB_SIMULATOR)
gaze_ctrl = icub.getIGazeControl()

rightarm_ctrl = icub.getPositionControl(ICUB_PARTS.RIGHT_ARM)

p = yarp.Vector(3)
p.set(0, -0.4)
p.set(1, 0.0)
p.set(2, 0.1)
gaze_ctrl.setTrackingMode(True)
gaze_ctrl.lookAtFixationPoint(p)


t1 = time.time()
rightarm_ctrl.move(target_joints=[10.06, 99.47, 5.31, 102.67, -13.50, -4.21], req_time=0.2, joints_list=[0, 1, 2, 3, 4, 5], waitMotionDone=True)
print time.time() - t1

raw_input()

t1 = time.time()
rightarm_ctrl.move(target_joints=[9.97, 99.63, 6.34, 97.23, -10.95, -3.11], req_time=0.2, joints_list=[0, 1, 2, 3, 4, 5], waitMotionDone=True)
print time.time() - t1
