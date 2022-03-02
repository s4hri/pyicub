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

import time
from pyicub.helper import iCub, JointPose, ICUB_PARTS

icub = iCub()
head_ctrl = icub.getPositionController(icub.parts[ICUB_PARTS.HEAD])
up = JointPose(target_joints=[30.0, 0.0, 0.0, 0.0, 0.0, 5.0])
down = JointPose(target_joints=[-30.0, 0.0, 0.0, 0.0, 0.0, 5.0])
home = JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 5.0])

t0 = time.perf_counter()
head_ctrl.move(up, req_time=3.0)
print("Time: ", time.perf_counter() - t0)
head_ctrl.move(down, req_time=3.0, timeout=1.0)
print("Time: ", time.perf_counter() - t0)
head_ctrl.move(up)
print("Time: ", time.perf_counter() - t0)
head_ctrl.move(home, speed=20.0)
print("Time: ", time.perf_counter() - t0)
