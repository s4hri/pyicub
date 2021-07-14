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

from pyicub.iCubHelper import iCub, JointPose, ICUB_PARTS, iCubTask

icub = iCub()

init_l = JointPose(ICUB_PARTS.LEFT_ARM, target_position=[0.0, 15.0, 0.0, 25.0, 0.0, 0.0, 0.0, 60.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
init_r = JointPose(ICUB_PARTS.RIGHT_ARM, target_position=[0.0, 15.0, 0.0, 25.0, 0.0, 0.0, 0.0, 60.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

up_r = JointPose(ICUB_PARTS.RIGHT_ARM, target_position=[-90.0, 20.0, 10.0, 90.0, 0.0, 0.0, 0.0, 60.0, 20.0, 20.0, 20.0, 10.0, 10.0, 10.0, 10.0, 10.0])
up_l = JointPose(ICUB_PARTS.LEFT_ARM, target_position=[-90.0, 20.0, 10.0, 90.0, 0.0, 0.0, 0.0, 60.0, 20.0, 20.0, 20.0, 10.0, 10.0, 10.0, 10.0, 10.0])

req1 = icub.move(init_l, req_time=1.0, in_parallel=True)
req2 = icub.move(init_r, req_time=1.0, in_parallel=True)

req1.wait_for_completed()
req2.wait_for_completed()

icub.move(up_r, req_time=1.0)
icub.move(up_l, req_time=1.0)

icub.close()
