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
move_part.py
============

This script controls the movement of the iCub humanoid robot's head and eyes.
It demonstrates how to define motion trajectories using multiple joint poses and execute
them sequentially.

Usage:
------
Run this script to move the iCub's head through a series of predefined positions and
coordinate the movement of its eyes.


"""

from pyicub.helper import iCub, JointPose, LimbMotion, ICUB_HEAD, ICUB_EYES

# Define head poses (Up, Down, Home)
head_up = JointPose(target_joints=[20.0, 0.0, 0.0, 0.0, 0.0, 0.0])
head_down = JointPose(target_joints=[-20.0, 0.0, 0.0, 0.0, 0.0, 0.0])
head_home = JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

# Create a motion trajectory for the head
head_motion = LimbMotion(ICUB_HEAD)
head_motion.createJointsTrajectory(head_up)
head_motion.createJointsTrajectory(head_down)
head_motion.createJointsTrajectory(head_home)

# Define eye movements
eyes_left = JointPose(target_joints=[0.0, 20.0, 5.0])
eyes_right = JointPose(target_joints=[0.0, -20.0, 5.0])
eyes_home = JointPose(target_joints=[0.0, 0.0, 0.0])

# Create a motion trajectory for the eyes
eyes_motion = LimbMotion(ICUB_EYES)
eyes_motion.createJointsTrajectory(eyes_left)
eyes_motion.createJointsTrajectory(eyes_right)
eyes_motion.createJointsTrajectory(eyes_home)

def move_head_and_eyes():
    """
    Moves the iCub's head and eyes through predefined motion sequences.

    Steps
    -----
    1. Moves the head through a sequence: "Up" -> "Down" -> "Home".
    2. Moves the eyes through a sequence: "Left" -> "Right" -> "Home".

    Example
    -------
    >>> move_head_and_eyes()

    Notes
    -----
    - The function sequentially executes predefined motion trajectories.
    - `LimbMotion` objects store multiple poses for smooth transitions.
    - The iCub executes head and eye movements independently.
    """
    # Create an instance of the iCub robot
    icub = iCub()

    # Execute head and eye movement sequences
    icub.movePart(head_motion)
    icub.movePart(eyes_motion)

if __name__ == "__main__":
    move_head_and_eyes()

