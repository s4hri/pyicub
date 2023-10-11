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


class GenericPoses(iCubFullbodyAction):

    def prepare(self):
        pose_up = JointPose(target_joints=[30.0, 0.0, 0.0, 0.0, 0.0, 5.0])
        pose_down = JointPose(target_joints=[-30.0, 0.0, 0.0, 0.0, 0.0, 5.0])
        pose_home = JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 5.0])
        
        step = self.createStep()
        lm = self.createLimbMotion(ICUB_PARTS.HEAD)
        up = self.createJointsTrajectory(pose_up, duration=2.0)
        down = self.createJointsTrajectory(pose_down, duration=2.0, timeout=1.0)
        home = self.createJointsTrajectory(pose_home, duration=2.0)
        lm.addJointsTrajectoryCheckpoint(up)
        lm.addJointsTrajectoryCheckpoint(down)
        lm.addJointsTrajectoryCheckpoint(home)
        step.setLimbMotion(lm)
        self.addStep(step)


action = GenericPoses()
icub = iCub()
action_id = icub.addAction(action)
icub.playAction(action_id)
icub.getPositionController(ICUB_PARTS.HEAD).setCustomWaitMotionDone(motion_complete_at=0.8)
icub.playAction(action_id)