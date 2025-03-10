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
lookat.py
===========

This script controls the gaze movement of the iCub humanoid robot. It demonstrates
how to direct the robot’s gaze to a specific 3D point and then reset its gaze
to an absolute angle.

Usage:
------
Run this script to move the iCub's gaze to a fixation point and then reset it to a neutral position.

"""

from pyicub.helper import iCub

# Create an instance of the iCub robot
icub = iCub()

def look_at_fixation_point(x: float = -1.0, y: float = -0.5, z: float = 1.0):
    """
    Directs the iCub’s gaze to a specific 3D fixation point in space.

    Parameters
    ----------
    x : float, optional
        The x-coordinate of the fixation point (default: -1.0).

    y : float, optional
        The y-coordinate of the fixation point (default: -0.5).

    z : float, optional
        The z-coordinate of the fixation point (default: 1.0).

    Example
    -------
    >>> look_at_fixation_point(-1.0, -0.5, 1.0)

    Notes
    -----
    - The fixation point is specified in 3D coordinates.
    - This function is useful for directing the robot’s attention to a specific location.
    """
    icub.gaze.lookAtFixationPoint(x, y, z)

def reset_gaze_to_neutral():
    """
    Resets the iCub's gaze to the absolute neutral angles.

    Example
    -------
    >>> reset_gaze_to_neutral()

    Notes
    -----
    - The gaze is reset by setting the azimuth (`azi`), elevation (`ele`),
      and vergence (`ver`) angles to zero.
    - This function is useful for returning the gaze to a predefined reference position.
    """
    icub.gaze.lookAtAbsAngles(azi=0.0, ele=0.0, ver=0.0)

if __name__ == "__main__":
    look_at_fixation_point()
    reset_gaze_to_neutral()

