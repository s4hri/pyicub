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


"""
lookat_timeout.py
===================

This script controls the gaze movement of the iCub humanoid robot with a timeout feature.
It demonstrates how to direct the robot’s gaze to absolute angles while enforcing a
timeout constraint on specific gaze operations.

Usage:
------
Run this script to move the iCub's gaze through a sequence of absolute angles
while ensuring that one of the movements respects a timeout limit.

"""

from pyicub.helper import iCub

# Create an instance of the iCub robot
icub = iCub()

def set_gaze_absolute(azi: float, ele: float, ver: float, timeout: float = None):
    """
    Moves the iCub's gaze to the specified absolute angles.

    Parameters
    ----------
    azi : float
        The azimuth angle in degrees (left/right movement).

    ele : float
        The elevation angle in degrees (up/down movement).

    ver : float
        The vergence angle in degrees (eye convergence).

    timeout : float, optional
        The maximum time allowed (in seconds) for the motion to complete.
        If None, the motion executes without a timeout (default: None).

    Example
    -------
    >>> set_gaze_absolute(10.0, 0.0, 0.0, timeout=1.0)

    Notes
    -----
    - If `timeout` is specified, the gaze movement must complete within the given duration.
    - This function is useful for controlling gaze operations in time-sensitive scenarios.
    """
    if timeout is not None:
        icub.gaze.lookAtAbsAngles(azi, ele, ver, timeout=timeout)
    else:
        icub.gaze.lookAtAbsAngles(azi, ele, ver)

def execute_gaze_sequence():
    """
    Executes a sequence of gaze movements, including a timeout-constrained operation.

    Steps
    -----
    1. Moves the gaze to a neutral position `(azi=0.0, ele=0.0, ver=0.0)`.
    2. Moves the gaze to `(azi=10.0, ele=0.0, ver=0.0)` with a timeout of 1 second.
    3. Moves the gaze to `(azi=-10.0, ele=0.0, ver=0.0)` without a timeout.
    4. Resets the gaze back to the neutral position.

    Example
    -------
    >>> execute_gaze_sequence()

    Notes
    -----
    - The timeout ensures that one of the gaze movements does not exceed the allowed time limit.
    - The function ensures a controlled, sequential execution of gaze motions.
    """
    set_gaze_absolute(0.0, 0.0, 0.0)  # Neutral position
    set_gaze_absolute(10.0, 0.0, 0.0, timeout=1.0)  # Move with timeout
    set_gaze_absolute(-10.0, 0.0, 0.0)  # Move without timeout
    set_gaze_absolute(0.0, 0.0, 0.0)  # Reset to neutral

if __name__ == "__main__":
    execute_gaze_sequence()

