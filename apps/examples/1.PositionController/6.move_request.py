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

from pyicub.helper import iCub, JointPose, LimbMotion, JointsTrajectoryCheckpoint, ICUB_PARTS

head_up = JointsTrajectoryCheckpoint(JointPose(target_joints=[20.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
head_down = JointsTrajectoryCheckpoint(JointPose(target_joints=[-20.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
head_home = JointsTrajectoryCheckpoint(JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))

torso_down = JointsTrajectoryCheckpoint(JointPose(target_joints=[0.0, 0.0, 20.0]))
torso_home = JointsTrajectoryCheckpoint(JointPose(target_joints=[0.0, 0.0, 0.0]))

icub = iCub()

head_motion = LimbMotion(ICUB_PARTS.HEAD)
head_motion.addCheckpoint(head_up)
head_motion.addCheckpoint(head_down)
head_motion.addCheckpoint(head_home)

torso_motion = LimbMotion(ICUB_PARTS.TORSO)
torso_motion.addCheckpoint(torso_down)
torso_motion.addCheckpoint(torso_home)

step = icub.createStep()
step.setLimbMotion(head_motion)
step.setLimbMotion(torso_motion)

[head_req, torso_req] = icub.moveStep(step)
print(head_req, torso_req)
icub.join_pending_requests(csv_output_filename='step.csv')
