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
move_parallel.py
================

This script controls both the head and torso movements of the iCub humanoid robot simultaneously.
It demonstrates how to retrieve position controllers for multiple parts, define joint poses, 
and execute parallel motion with synchronized execution.

Usage:
------
Run this script to move the iCub's head and torso simultaneously to predefined positions 
and then return them to their initial positions.

"""

from pyicub.helper import iCub, JointPose, ICUB_HEAD, ICUB_TORSO

# Create an instance of the iCub robot
icub = iCub()

# Retrieve position controllers for the iCub's head and torso
head_ctrl = icub.getPositionController(ICUB_HEAD)
torso_ctrl = icub.getPositionController(ICUB_TORSO)

# Define the "up" pose for the head
head_up = JointPose(target_joints=[20.0, 0.0, 0.0, 0.0, 0.0, 0.0])

# Define the "home" pose for the head (neutral position)
head_home = JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

# Define the "down" pose for the torso
torso_down = JointPose(target_joints=[0.0, 0.0, 20.0])

# Define the "home" pose for the torso (neutral position)
torso_home = JointPose(target_joints=[0.0, 0.0, 0.0])

def move_head_and_torso_parallel(req_time_head: float = 1.0, req_time_torso: float = 5.0, timeout: float = 10.0):
    """
    Moves the iCub's head and torso simultaneously to predefined positions and then back to their initial positions.

    Parameters
    ----------
    req_time_head : float, optional
        The requested time (in seconds) for the head motion to complete. Default is 1.0 seconds.
    
    req_time_torso : float, optional
        The requested time (in seconds) for the torso motion to complete. Default is 5.0 seconds.

    timeout : float, optional
        The maximum time allowed (in seconds) for the motion to complete before timeout occurs. Default is 10.0 seconds.

    Steps
    -----
    1. Move both the head and torso to their "home" positions.
    2. Move the head to the "up" position and the torso to the "down" position simultaneously.
    3. Wait for both motions to complete.
    4. Move both the head and torso back to their "home" positions.

    Example
    -------
    >>> move_head_and_torso_parallel(req_time_head=1.0, req_time_torso=5.0, timeout=10.0)

    Notes
    -----
    - The movements of the head and torso are executed in parallel.
    - The function ensures that both motions are completed before proceeding.
    - The timeout prevents the robot from remaining in an unfinished movement state.
    """
    # Move head and torso to home position
    head_ctrl.move(head_home)
    torso_ctrl.move(torso_home)

    # Move head up and torso down in parallel
    head_ctrl.move(head_up, req_time=req_time_head, waitMotionDone=False)
    torso_ctrl.move(torso_down, req_time=req_time_torso, waitMotionDone=False)

    # Wait for both motions to complete
    head_ctrl.waitMotionDone(timeout=timeout)
    torso_ctrl.waitMotionDone(timeout=timeout)

    # Move head and torso back to home position
    head_ctrl.move(head_home)
    torso_ctrl.move(torso_home)

if __name__ == "__main__":
    move_head_and_torso_parallel()

