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

import os

class CustomAction(iCubFullbodyAction):

    def prepare(self):
        step1 = self.createStep()        
        cc = self.createCustomCall(target="gaze.lookAtAbsAngles", args=(0.0, 15.0, 0.0,))
        step1.setCustomCall(cc)
        cc = self.createCustomCall(target="emo.neutral")
        step1.setCustomCall(cc)
        self.addStep(step1)

        step2 = self.createStep()
        cc = self.createCustomCall(target="gaze.lookAtAbsAngles", args=(0.0, 0.0, 0.0,))
        step2.setCustomCall(cc)
        cc = self.createCustomCall(target="emo.smile")
        step2.setCustomCall(cc)
        self.addStep(step2)


action = CustomAction()
icub = iCub()
action_id = icub.addAction(action)
icub.playAction(action_id)
icub.exportAction(action_id=action_id, path=os.path.join(os.getcwd(), 'json'))
