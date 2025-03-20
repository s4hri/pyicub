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
lookat_portmonitor.py
=======================

This script controls the gaze movement of the iCub humanoid robot using YARP port monitoring.
It demonstrates how to monitor gaze angles and trigger specific actions when the gaze reaches 
a predefined position.

Usage:
------
Run this script to move the iCub's gaze while monitoring its movement 
and triggering events based on detected positions.

"""

from pyicub.helper import iCub

# Define three gaze positions
DOWN = [0.0, -15.0, 3.0]  # Looking downward
ZERO = [0.0, 0.0, 3.0]    # Neutral position
UP = [0.0, 15.0, 3.0]     # Looking upward

def af1(values):
    """
    Activation function for port monitoring. 

    This function checks if the iCub's gaze is close to the `ZERO` position.

    Parameters
    ----------
    values : list
        A list of strings representing the last read values from the monitored YARP port.

    Returns
    -------
    bool
        `True` if the gaze is close to `ZERO`, otherwise `False`.

    Example
    -------
    >>> af1(["0.0 -0.5 3.0"])
    True
    """
    lastread = values[-1].split(' ')
    if abs(ZERO[1] - float(lastread[1])) < 2:
        return True
    return False

def cb1():
    """
    Callback function triggered when the iCub's gaze reaches the `ZERO` position.

    Example
    -------
    >>> cb1()
    Watching at ZERO detected!
    """
    print("Watching at ZERO detected!")

def monitor_gaze():
    """
    Monitors the iCub's gaze and triggers an event when it reaches the `ZERO` position.

    Steps
    -----
    1. Initializes an instance of the iCub robot.
    2. Sets up a YARP port monitor on the gaze control output.
    3. Moves the gaze to the `UP` position.
    4. Alternates between `DOWN` and `UP` positions three times.
    5. Resets the gaze to `ZERO`.
    6. Closes the YARP connection.

    Example
    -------
    >>> monitor_gaze()

    Notes
    -----
    - The YARP port monitor continuously checks gaze positions.
    - The `cb1` callback is executed when the gaze is near `ZERO`.
    - This function ensures dynamic event-based gaze monitoring.
    """
    icub = iCub()

    # Set up the YARP port monitor
    icub.portmonitor("/iKinGazeCtrl/angles:o", activate_function=af1, callback=cb1)

    # Move gaze to UP position
    icub.gaze.lookAtAbsAngles(UP[0], UP[1], UP[2])

    # Alternate gaze between DOWN and UP positions
    for _ in range(3):
        icub.gaze.lookAtAbsAngles(DOWN[0], DOWN[1], DOWN[2])
        icub.gaze.lookAtAbsAngles(UP[0], UP[1], UP[2])

    # Reset gaze to ZERO position
    icub.gaze.lookAtAbsAngles(0.0, 0.0, 0.0)

    # Close YARP connection
    icub.close()

if __name__ == "__main__":
    monitor_gaze()

