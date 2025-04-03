# BSD 2-Clause License
#
# Copyright (c) 2025, Social Cognition in Human-Robot Interaction,
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
observe.py
============

This script controls an iCub robot to systematically observe and scan two defined regions:
1. Workspace area (e.g., a table surface).
2. General scene area (e.g., space in front of the robot).

Usage:
------
python observe.py
"""

# Import the helper class to interface with iCub robot
from pyicub.helper import iCub

# Main function to control robot observation
def observe():
    # Initialize an instance of the iCub robot
    icub = iCub()

    # Define parameters for observing the workspace (e.g., table surface)
    Table_center = (-1.0, 0.0, 0.0)     # Coordinates for the center of the workspace
    Table_width = 0.6                   # Width of the workspace area
    Table_depth = 0.4                   # Depth of the workspace area

    # Common parameters for observation
    num_points = 10                     # Number of fixation points during observation
    fixation_time = 1.0                 # Time (in seconds) the robot fixates on each point
    lookat_point_timeout = 5.0          # Timeout (in seconds) for reaching a fixation point

    # Define parameters for observing the general scene area (above the workspace)
    Area_center = (-1.0, 0.0, 0.5)      # Coordinates for the center of the observation area
    Area_width = 1.0                    # Width of the observation area
    Area_height = 0.5                   # Height of the observation area

    # Command the robot to observe points within the workspace (table surface)
    icub.attention.observe_workspace(
        center=Table_center,
        width=Table_width,
        depth=Table_depth,
        num_points=num_points,
        fixation_time=fixation_time,
        lookat_point_timeout=lookat_point_timeout,
        waitMotionDone=True             # Wait until motion is completed before proceeding
    )

    # Command the robot to observe points within the general scene area
    icub.attention.observe_scene(
        center=Area_center,
        width=Area_width,
        height=Area_height,
        num_points=num_points,
        fixation_time=fixation_time,
        lookat_point_timeout=lookat_point_timeout,
        waitMotionDone=True             # Wait until motion is completed before proceeding
    )

# Execute the observation behavior if this script is run as main
if __name__ == "__main__":
    observe()