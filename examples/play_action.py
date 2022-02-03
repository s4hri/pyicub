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

from pyicub.helper import iCub, iCubFullbodyAction
import json

icub = iCub()

from pyicub.helper import JointPose, JointsTrajectoryCheckpoint, LimbMotion, ICUB_PARTS, GazeMotion, iCubFullbodyAction, PyiCubCustomCall
import json

arm_down = JointPose(target_joints=[0.0, 15.0, 0.0, 25.0, 0.0, 0.0, 0.0, 60.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
arm_up = JointPose(target_joints=[-90.0, 20.0, 10.0, 90.0, 0.0, 0.0, 0.0, 60.0, 20.0, 20.0, 20.0, 10.0, 10.0, 10.0, 10.0, 10.0])

up = JointsTrajectoryCheckpoint(arm_up, duration=1.0, timeout=2.0)
down = JointsTrajectoryCheckpoint(arm_down, duration=1.0, timeout=2.0)

m1 = LimbMotion(ICUB_PARTS.RIGHT_ARM)
m1.addCheckpoint(up)
m1.addCheckpoint(down)

m2 = LimbMotion(ICUB_PARTS.LEFT_ARM)
m2.addCheckpoint(up)
m2.addCheckpoint(down)

g = GazeMotion(lookat_method="lookAtAbsAngles")
g.addCheckpoint([20.0, 0.0, 0.0])
g.addCheckpoint([-20.0, 0.0, 0.0])
g.addCheckpoint([0.0, 0.0, 0.0])

action = iCubFullbodyAction()

c = PyiCubCustomCall(target="gaze.lookAtAbsAngles", args=(0.0, 15.0, 0.0,))
d = PyiCubCustomCall(target="emo.neutral")
e = PyiCubCustomCall(target="emo.smile")

step1 = action.addStep()
step2 = action.addStep()
step3 = action.addStep()

step1.setLimbMotion(m1)
step1.addCustomCall(c)
step1.addCustomCall(d)

step2.setLimbMotion(m2)

step3.setGazeMotion(g)
step3.setLimbMotion(m1)
step3.setLimbMotion(m2)
step3.addCustomCall(e)

action.exportJSONFile('json/complete_action.json')

imported_action = iCubFullbodyAction(JSON_file='json/complete_action.json')
icub.play(imported_action)
icub.close()
