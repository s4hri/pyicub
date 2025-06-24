# BSD 2-Clause License
#
# Copyright (c) 2023, Social Cognition in Human-Robot Interaction,
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
move_speed_scaling.py
===========================

This script controls the movement of the iCub humanoid robot's head and torso using a structured
full-body step motion. The action is executed applying a speed scaling over the default joints speeds.

Usage:
------
Run this script to execute a predefined movement sequence for the iCub's head and torso with the desired `PositionController.SPEED_SCALING`


"""

from pyicub.helper import iCub, JointPose, LimbMotion, ICUB_HEAD, ICUB_TORSO, iCubFullbodyStep
from pyicub.controllers.position import PositionController

PositionController.SPEED_SCALING = 0.8

# from `move_request.py` example
class HeadTorsoStep(iCubFullbodyStep):
    """
    Defines a full-body step for the iCub humanoid robot involving both head and torso movements.

    This class groups multiple limb motions into a single step, ensuring synchronization
    between different body parts.

    Methods
    -------
    prepare()
        Initializes the step by creating limb motion trajectories for the head and torso.
    """

    def prepare(self):
        """
        Prepares the movement sequences for the head and torso.

        Steps
        -----
        1. Creates a limb motion trajectory for the head.
        2. Creates a limb motion trajectory for the torso.
        3. Adds predefined poses for each body part.

        Example
        -------
        >>> step = HeadTorsoStep()
        >>> step.prepare()
        """
        # Define head poses (Up, Down, Home)
        head_up = JointPose(target_joints=[20.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        head_down = JointPose(target_joints=[-20.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        head_home = JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Define torso poses (Down, Home)
        torso_down = JointPose(target_joints=[0.0, 0.0, 20.0])
        torso_home = JointPose(target_joints=[0.0, 0.0, 0.0])

        # Create a motion trajectory for the head
        head_motion = self.createLimbMotion(ICUB_HEAD)
        head_motion.createJointsTrajectory(head_up)
        head_motion.createJointsTrajectory(head_down)
        head_motion.createJointsTrajectory(head_home)

        # Create a motion trajectory for the torso
        torso_motion = self.createLimbMotion(ICUB_TORSO)
        torso_motion.createJointsTrajectory(torso_down)
        torso_motion.createJointsTrajectory(torso_home)

# from `move_request.py` example
def execute_fullbody_step_with_request():
    """
    Executes a predefined full-body step for the iCub's head and torso and retrieves motion requests.

    Steps
    -----
    1. Initializes an iCub instance.
    2. Creates and prepares a `HeadTorsoStep` motion sequence.
    3. Executes the movement step on the iCub.
    4. Retrieves the motion requests for debugging and monitoring.

    Returns
    -------
    list
        A list of motion requests containing information about the executed movements.

    Example
    -------
    >>> requests = execute_fullbody_step_with_request()
    >>> print(requests)

    Notes
    -----
    - The step is structured using `iCubFullbodyStep` for better modularity.
    - Motion requests provide insights into the robot's behavior during execution.
    - The function ensures that both head and torso movements are synchronized.
    """
    # Create an instance of the iCub robot
    icub = iCub()

    # Create and execute the full-body step
    step = HeadTorsoStep()
    motion_requests = icub.moveStep(step)

    # Print the returned motion requests
    print(motion_requests)
    return motion_requests

if __name__ == "__main__":
    execute_fullbody_step_with_request()

