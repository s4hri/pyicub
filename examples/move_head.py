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

import time
from pyicub.helper import iCub, JointPose, ICUB_PARTS

icub = iCub()
head_ctrl = icub.getPositionController(icub.parts[ICUB_PARTS.HEAD])
up = JointPose(target_joints=[30.0, 0.0, 0.0, 0.0, 0.0, 5.0])
down = JointPose(target_joints=[-30.0, 0.0, 0.0, 0.0, 0.0, 5.0])
home = JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 5.0])
"""
t0 = time.perf_counter()
head_ctrl.move(up, req_time=3.0)
print("Time: ", time.perf_counter() - t0)
head_ctrl.move(down, req_time=3.0, timeout=1.0)
print("Time: ", time.perf_counter() - t0)
head_ctrl.move(up)
print("Time: ", time.perf_counter() - t0)
head_ctrl.move(home, speed=20.0)
print("Time: ", time.perf_counter() - t0)
"""
