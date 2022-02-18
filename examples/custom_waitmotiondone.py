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

from pyicub.helper import iCub, JointPose, JointsTrajectoryCheckpoint, LimbMotion, ICUB_PARTS, iCubFullbodyAction

icub = iCub()

icub.getPositionController(icub.parts['head']).setCustomWaitMotionDone(min_joints_dist=20)
up = JointsTrajectoryCheckpoint(JointPose(target_joints=[30.0, 0.0, 0.0, 0.0, 0.0, 5.0]), duration=3.0)
down = JointsTrajectoryCheckpoint(JointPose(target_joints=[-30.0, 0.0, 0.0, 0.0, 0.0, 5.0]), duration=3.0, timeout=1.0)
home = JointsTrajectoryCheckpoint(JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 5.0]), duration=3.0)
    
example_motion = LimbMotion(ICUB_PARTS.HEAD)
example_motion.addCheckpoint(up)
example_motion.addCheckpoint(down)
example_motion.addCheckpoint(home)
    
action = iCubFullbodyAction(name='moveHeadUpAndDown')
step = action.addStep()
step.setLimbMotion(example_motion)
action.exportJSONFile('json/move_head.json')
    
icub.play(action)
icub.getPositionController(icub.parts['head']).unsetCustomWaitMotionDone()
icub.play(action)