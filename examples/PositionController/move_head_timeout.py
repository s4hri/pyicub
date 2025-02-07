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


"""
move_head_timeout.py
====================

This script controls the head movement of the iCub humanoid robot with a timeout feature.
It demonstrates how to retrieve the position controller for the head, define joint poses, 
and execute timed head movements with a specified timeout.

Usage:
------
Run this script to move the iCub's head to an "up" position and then return it to the "home" position 
within a specific timeout period.


"""

from pyicub.helper import iCub, JointPose, ICUB_HEAD

# Create an instance of the iCub robot
icub = iCub()

# Retrieve the position controller for the iCub's head
head_ctrl = icub.getPositionController(ICUB_HEAD)

# Define the "up" pose for the head
up = JointPose(target_joints=[20.0, 0.0, 0.0, 0.0, 0.0, 0.0])

# Define the "home" pose for the head (neutral position)
home = JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

def move_head_with_timeout(req_time: float = 1.0, timeout: float = 0.5):
    """
    Moves the iCub's head to the "up" position and then back to the "home" position within a specified timeout.

    Parameters
    ----------
    req_time : float, optional
        The requested time (in seconds) for the motion to complete. Default is 1.0 seconds.
    
    timeout : float, optional
        The maximum time allowed (in seconds) for the motion to complete before timeout occurs. Default is 0.5 seconds.

    Steps
    -----
    1. Move the head to the `up` position within the requested time.
    2. If the movement does not complete within the timeout period, it stops.
    3. Move the head back to the `home` position with the same timeout settings.

    Example
    -------
    >>> move_head_with_timeout(req_time=1.0, timeout=0.5)

    Notes
    -----
    - The timeout ensures that the robot does not get stuck in an unfinished movement.
    - The `req_time` is the expected duration for the motion to complete.
    - If `timeout` is exceeded, the motion is forcefully stopped.
    """
    head_ctrl.move(up, req_time=req_time, timeout=timeout)
    head_ctrl.move(home, req_time=req_time, timeout=timeout)

if __name__ == "__main__":
    move_head_with_timeout()

