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

from pyicub.helper import iCub, JointPose, JointsTrajectoryCheckpoint, LimbMotion, ICUB_PARTS, GazeMotion, iCubFullbodyAction, PyiCubCustomCall, iCubFullbodyStep


class CompleteAction(iCubFullbodyAction):

    def prepare(self):
        arm_down = JointPose(target_joints=[0.0, 15.0, 0.0, 25.0, 0.0, 0.0, 0.0, 60.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        arm_up = JointPose(target_joints=[-90.0, 20.0, 10.0, 90.0, 0.0, 0.0, 0.0, 60.0, 20.0, 20.0, 20.0, 10.0, 10.0, 10.0, 10.0, 10.0])

        step1 = self.addStep()
        m1 = step1.setLimbMotion(ICUB_PARTS.RIGHT_ARM)
        m1.addCheckpoint(arm_up, duration=1.0)
        m1.addCheckpoint(arm_down, duration=1.0)
        step1.setCustomCall(target="gaze.lookAtAbsAngles", args=(0.0, 15.0, 0.0,))
        step1.setCustomCall(target="emo.neutral")

        step2 = self.addStep()
        m2 = step2.setLimbMotion(ICUB_PARTS.LEFT_ARM)
        m2.addCheckpoint(arm_up, duration=1.0)
        m2.addCheckpoint(arm_down, duration=1.0)
        step2.setLimbMotion(m2)

        step3 = self.addStep(offset_ms=500)
        g = step3.setGazeMotion(lookat_method="lookAtAbsAngles")
        g.addCheckpoint([20.0, 0.0, 0.0])
        g.addCheckpoint([-20.0, 0.0, 0.0])
        g.addCheckpoint([0.0, 0.0, 0.0])
        m3 = step3.setLimbMotion(ICUB_PARTS.RIGHT_ARM)
        m3.addCheckpoint(arm_up, duration=1.0)
        m3.addCheckpoint(arm_down, duration=1.0)
        m4 = step3.setLimbMotion(ICUB_PARTS.LEFT_ARM)
        m4.addCheckpoint(arm_up, duration=1.0)
        m4.addCheckpoint(arm_down, duration=1.0)
        step3.setCustomCall(target="emo.smile")

action = CompleteAction()
icub = iCub()
action_id = icub.addAction(action)
icub.playAction(action_id)
icub.exportAction(action_id=action_id, path=os.path.join(os.getcwd(), 'json'))

