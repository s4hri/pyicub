# BSD 2-Clause License
#
# Copyright (c) 2024, Social Cognition in Human-Robot Interaction,
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

from pyicub.helper import iCub, JointPose, ICUB_HEAD, iCubFullbodyAction, iCubFullbodyStep

import os

class Step(iCubFullbodyStep):

    def prepare(self):

        pose_up = JointPose(target_joints=[20.0, 0.0, 0.0, 0.0, 0.0, 5.0])
        pose_down = JointPose(target_joints=[-20.0, 0.0, 0.0, 0.0, 0.0, 5.0])
        pose_home = JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 5.0])

        motion = self.createLimbMotion(ICUB_HEAD)
        motion.createJointsTrajectory(pose_up, duration=3.0)
        motion.createJointsTrajectory(pose_down, duration=3.0)
        motion.createJointsTrajectory(pose_home, duration=3.0)

class HeadActionE(iCubFullbodyAction):

    def prepare(self):
        step = Step()
        self.addStep(step)

class Step1(iCubFullbodyStep):

    def prepare(self):
        self.createCustomCall(target="gaze.lookAtAbsAngles", args=(0.0, 15.0, 0.0,))
        self.createCustomCall(target="emo.neutral")

class Step2(iCubFullbodyStep):

    def prepare(self):
        self.createCustomCall(target="gaze.lookAtAbsAngles", args=(0.0, 0.0, 0.0,))
        self.createCustomCall(target="emo.smile")

class CustomAction(iCubFullbodyAction):

    def prepare(self):
        self.addStep(Step1())
        self.addStep(Step2())
    
action = HeadActionE()
custom_action = CustomAction()
action.addAction(custom_action)

icub = iCub()
action_id = icub.addAction(action)
icub.playAction(action_id)
icub.exportAction(action_id=action_id, path=os.path.join(os.getcwd(), 'json'))
