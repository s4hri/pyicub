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

from pyicub.helper import iCub, JointPose, ICUB_HEAD, ICUB_TORSO

icub = iCub()
head_ctrl = icub.getPositionController(ICUB_HEAD)
torso_ctrl = icub.getPositionController(ICUB_TORSO)

head_up = JointPose(target_joints=[20.0, 0.0, 0.0, 0.0, 0.0, 0.0])
head_home = JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

torso_down = JointPose(target_joints=[0.0, 0.0, 20.0])
torso_home = JointPose(target_joints=[0.0, 0.0, 0.0])

head_ctrl.move(head_home)
torso_ctrl.move(torso_home)

head_ctrl.move(head_up, req_time=1.0, waitMotionDone=False)
torso_ctrl.move(torso_down, req_time=5.0, waitMotionDone=False)

head_ctrl.waitMotionDone(timeout=10.0)
torso_ctrl.waitMotionDone(timeout=10.0)

head_ctrl.move(head_home)
torso_ctrl.move(torso_home)

