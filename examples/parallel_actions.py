# BSD 2-Clause License
#
# Copyright (c) 2022, Social Cognition in Human-Robot Interaction,
#                     Istituto Italiano di Tecnologia, Genova
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from pyicub.helper import iCub, JointPose, JointsTrajectoryCheckpoint, LimbMotion, ICUB_PARTS, GazeMotion, iCubFullbodyAction

icub = iCub()
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

step1 = action.addStep()
step2 = action.addStep()
step3 = action.addStep(offset_ms=2000)

step1.setLimbMotion(m1)

step2.setLimbMotion(m2)

step3.setGazeMotion(g)
step3.setLimbMotion(m1)
step3.setLimbMotion(m2)

icub.play(action)
