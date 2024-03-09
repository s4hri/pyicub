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

from pyicub.helper import iCub, JointPose, LimbMotion, iCubFullbodyAction, iCubFullbodyStep, ICUB_RIGHTARM_FULL, ICUB_LEFTARM_FULL

import os

arm_down = JointPose(target_joints=[0.0, 15.0, 0.0, 25.0, 0.0, 0.0, 0.0, 60.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
arm_up = JointPose(target_joints=[-90.0, 20.0, 10.0, 90.0, 0.0, 0.0, 0.0, 60.0, 20.0, 20.0, 20.0, 10.0, 10.0, 10.0, 10.0, 10.0])

right_arm_motion = LimbMotion(ICUB_RIGHTARM_FULL)
right_arm_motion.createJointsTrajectory(arm_up, duration=1.0)
right_arm_motion.createJointsTrajectory(arm_down, duration=1.0)

left_arm_motion = LimbMotion(ICUB_LEFTARM_FULL)
left_arm_motion.createJointsTrajectory(arm_up, duration=1.0)
left_arm_motion.createJointsTrajectory(arm_down, duration=1.0)

class Step1(iCubFullbodyStep):

    def prepare(self):
        self.setLimbMotion(right_arm_motion)
        self.setLimbMotion(left_arm_motion)
        self.createCustomCall(target="gaze.lookAtAbsAngles", args=(0.0, 15.0, 0.0,))
        self.createCustomCall(target="emo.neutral")

class Step2(iCubFullbodyStep):

    def prepare(self):
        self.setLimbMotion(left_arm_motion)

class Step3(iCubFullbodyStep):

    def prepare(self):
        g = self.createGazeMotion(lookat_method="lookAtAbsAngles")
        g.addCheckpoint([20.0, 0.0, 0.0])
        g.addCheckpoint([-20.0, 0.0, 0.0])
        g.addCheckpoint([0.0, 0.0, 0.0])

        self.setLimbMotion(right_arm_motion)
        self.setLimbMotion(left_arm_motion)
        self.createCustomCall(target="emo.smile")

class CompleteAction(iCubFullbodyAction):

    def prepare(self):
        self.addStep(Step1())
        self.addStep(Step2())
        self.addStep(Step3(offset_ms=500))

action = CompleteAction()
icub = iCub()
action_id = icub.addAction(action)
icub.playAction(action_id)
icub.exportAction(action_id=action_id, path=os.path.join(os.getcwd(), 'json'))

