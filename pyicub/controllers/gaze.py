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

import os
import yarp
import pyicub.utils as utils

"""
This script provides a GazeController class to manage the gaze control of a robot using YARP.

It includes functionalities to control the gaze direction, block and clear eye and neck movements, and set parameters for the gaze control.
"""

class GazeControllerPolyDriver:
    """
    GazeControllerPolyDriver is a helper class to manage the YARP PolyDriver for the gaze controller.

    Attributes:
        __pid__ (str): Process ID (unique identifier).
        __props__ (yarp.Property): Properties for the YARP PolyDriver.
        __driver__ (yarp.PolyDriver): The YARP PolyDriver instance.
    """

    def __init__(self, robot):
        """
        Initializes the GazeControllerPolyDriver with the given robot name.

        Args:
            robot (str): The name of the robot.
        """
        self.__pid__ = str(os.getpid())  # Get the process ID (unique identifier)
        self.__props__ = yarp.Property()  # Create a YARP Property object to hold the driver properties
        self.__props__.put("robot", robot)  # Set the robot name in the properties
        self.__props__.put("device", "gazecontrollerclient")  # Set the device type to gaze controller client
        self.__props__.put("local", "/pyicub/gaze/" + self.__pid__)  # Set the local port name using the process ID
        self.__props__.put("remote", "/iKinGazeCtrl")  # Set the remote port name for the gaze controller
        self.__driver__ = yarp.PolyDriver(self.__props__)  # Create the YARP PolyDriver with the specified properties

    def __del__(self):
        """
        Destructor to close the YARP PolyDriver.
        """
        self.__driver__.close()  # Close the YARP PolyDriver

    @property
    def properties(self):
        """
        Returns the properties of the YARP PolyDriver.

        Returns:
            yarp.Property: The properties of the YARP PolyDriver.
        """
        return self.__props__  # Return the properties

    def getDriver(self):
        """
        Returns the YARP PolyDriver instance.

        Returns:
            yarp.PolyDriver: The YARP PolyDriver instance.
        """
        return self.__driver__  # Return the YARP PolyDriver instance

        

class GazeController:
    """
    GazeController manages the gaze control of a robot using YARP.

    Attributes:
        __logger__ (Logger): Logger instance for logging information.
        __driver__ (GazeControllerPolyDriver): Instance of GazeControllerPolyDriver to manage the YARP PolyDriver.
        __mot_id__ (int): Motion ID counter.
        __IGazeControl__ (IGazeControl): Interface for gaze control.
    """

    def __init__(self, robot, logger):
        """
        Initializes the GazeController with the given robot name and logger.

        Args:
            robot (str): The name of the robot.
            logger (Logger): Logger instance for logging information.
        """
        self.__logger__ = logger
        self.__driver__ = GazeControllerPolyDriver(robot)
        self.__mot_id__ = 0
        self.__IGazeControl__ = None

    def isValid(self):
        """
        Checks if the PolyDriver is valid.

        Returns:
            bool: True if the PolyDriver is valid, False otherwise.
        """
        return self.PolyDriver.isValid()

    def init(self):
        """
        Initializes the gaze control interface and stops any ongoing control.
        """
        self.__IGazeControl__ = self.PolyDriver.viewIGazeControl()
        self.__IGazeControl__.setTrackingMode(False)
        self.__IGazeControl__.stopControl()
        self.clearNeck()
        self.clearEyes()

    def __del__(self):
        """
        Destructor to close the PolyDriver.
        """
        self.PolyDriver.close()

    @property
    def PolyDriver(self):
        """
        Returns the YARP PolyDriver instance.

        Returns:
            yarp.PolyDriver: The YARP PolyDriver instance.
        """
        return self.__driver__.getDriver()

    @property
    def IGazeControl(self):
        """
        Returns the gaze control interface.

        Returns:
            IGazeControl: The gaze control interface.
        """
        return self.__IGazeControl__

    def __lookAtAbsAngles__(self, angles, waitMotionDone=True, timeout=0.0):
        """
        Looks at the specified absolute angles.

        Args:
            angles (yarp.Vector): The angles to look at.
            waitMotionDone (bool): Whether to wait for the motion to complete.
            timeout (float): Timeout for waiting for the motion to complete.

        Raises:
            TimeoutError: If the motion does not complete within the timeout period.
        """
        self.__mot_id__ += 1
        self.__logger__.info("""Looking at angles <%d> STARTED!
                                 angles=%s, waitMotionDone=%s, timeout=%s""" % (self.__mot_id__, str([angles[0], angles[1], angles[2]]), str(waitMotionDone), str(timeout)) )
        self.IGazeControl.lookAtAbsAngles(angles)
        res = True
        if waitMotionDone is True:
            res = self.waitMotionDone(timeout=timeout)
        if res:
            self.__logger__.info("""Looking at angles <%d> COMPLETED!
                                    angles=%s, waitMotionDone=%s, timeout=%s""" % (self.__mot_id__, str([angles[0], angles[1], angles[2]]), str(waitMotionDone), str(timeout)) )
        else:
            self.__logger__.warning("""Looking at angles <%d> TIMEOUT!
                                       angles=%s, waitMotionDone=%s, timeout=%s""" % (self.__mot_id__, str([angles[0], angles[1], angles[2]]), str(waitMotionDone), str(timeout)) )

    def __lookAtRelAngles__(self, angles, waitMotionDone=True, timeout=0.0):
        """
        Looks at the specified relative angles.

        Args:
            angles (yarp.Vector): The relative angles to look at.
            waitMotionDone (bool): Whether to wait for the motion to complete.
            timeout (float): Timeout for waiting for the motion to complete.

        Raises:
            TimeoutError: If the motion does not complete within the timeout period.
        """
        self.__mot_id__ += 1
        self.__logger__.info("""Looking at rel angles <%d> STARTED!
                                 angles=%s, waitMotionDone=%s, timeout=%s""" % (self.__mot_id__, str([angles[0], angles[1], angles[2]]), str(waitMotionDone), str(timeout)) )
        self.IGazeControl.lookAtRelAngles(angles)
        res = True
        if waitMotionDone is True:
            res = self.waitMotionDone(timeout=timeout)
        if res:
            self.__logger__.info("""Looking at rel angles <%d> COMPLETED!
                                    angles=%s, waitMotionDone=%s, timeout=%s""" % (self.__mot_id__, str([angles[0], angles[1], angles[2]]), str(waitMotionDone), str(timeout)) )
        else:
            self.__logger__.warning("""Looking at rel angles <%d> TIMEOUT!
                                        angles=%s, waitMotionDone=%s, timeout=%s""" % (self.__mot_id__, str([angles[0], angles[1], angles[2]]), str(waitMotionDone), str(timeout)) )

    def blockEyes(self, vergence):
        """
        Blocks the eyes at the specified vergence.

        Args:
            vergence (float): The vergence angle to block the eyes at.
        """
        self.IGazeControl.blockEyes(vergence)

    def blockNeck(self):
        """
        Blocks the neck movements.
        """
        self.IGazeControl.blockNeckYaw()
        self.IGazeControl.blockNeckRoll()
        self.IGazeControl.blockNeckPitch()

    def clearEyes(self):
        """
        Clears the eye movements.
        """
        self.IGazeControl.clearEyes()

    def clearNeck(self):
        """
        Clears the neck movements.
        """
        self.IGazeControl.clearNeckYaw()
        self.IGazeControl.clearNeckRoll()
        self.IGazeControl.clearNeckPitch()

    def lookAtAbsAngles(self, azi, ele, ver, waitMotionDone=True, timeout=0.0):
        """
        Looks at the specified absolute angles.

        Args:
            azi (float): Azimuth angle.
            ele (float): Elevation angle.
            ver (float): Vergence angle.
            waitMotionDone (bool): Whether to wait for the motion to complete.
            timeout (float): Timeout for waiting for the motion to complete.
        """
        angles = yarp.Vector(3)
        angles.set(0, azi)
        angles.set(1, ele)
        angles.set(2, ver)
        self.__lookAtAbsAngles__(angles, waitMotionDone, timeout)

    def lookAtRelAngles(self, azi, ele, ver, waitMotionDone=True, timeout=0.0):
        """
        Looks at the specified relative angles.

        Args:
            azi (float): Relative azimuth angle.
            ele (float): Relative elevation angle.
            ver (float): Relative vergence angle.
            waitMotionDone (bool): Whether to wait for the motion to complete.
            timeout (float): Timeout for waiting for the motion to complete.
        """
        angles = yarp.Vector(3)
        angles.set(0, azi)
        angles.set(1, ele)
        angles.set(2, ver)
        self.__lookAtRelAngles__(angles, waitMotionDone, timeout)

    def lookAtFixationPoint(self, x, y, z, waitMotionDone=True, timeout=0.0):
        """
        Looks at the specified fixation point.

        Args:
            x (float): X coordinate of the fixation point.
            y (float): Y coordinate of the fixation point.
            z (float): Z coordinate of the fixation point.
            waitMotionDone (bool): Whether to wait for the motion to complete.
            timeout (float): Timeout for waiting for the motion to complete.
        """
        p = yarp.Vector(3)
        p.set(0, x)
        p.set(1, y)
        p.set(2, z)
        angles = yarp.Vector(3)
        self.IGazeControl.getAnglesFrom3DPoint(p, angles)
        self.__lookAtAbsAngles__(angles, waitMotionDone, timeout)

    def reset(self):
        """
        Resets the gaze control by clearing the eyes and neck movements.
        """
        self.clearEyes()
        self.clearNeck()

    def setParams(self, neck_tt, eyes_tt):
        """
        Sets the trajectory times for the neck and eyes.

        Args:
            neck_tt (float): Trajectory time for the neck.
            eyes_tt (float): Trajectory time for the eyes.
        """
        self.IGazeControl.setNeckTrajTime(neck_tt)
        self.IGazeControl.setEyesTrajTime(eyes_tt)

    def setTrackingMode(self, mode):
        """
        Sets the tracking mode.

        Args:
            mode (bool): True to enable tracking mode, False to disable.
        """
        self.IGazeControl.setTrackingMode(mode)

    def waitMotionDone(self, period=0.1, timeout=0.0):
        """
        Waits for the motion to complete.

        Args:
            period (float): Period to check the motion status.
            timeout (float): Timeout for waiting for the motion to complete.

        Returns:
            bool: True if the motion completed, False otherwise.
        """
        return self.IGazeControl.waitMotionDone(period=period, timeout=timeout)

    def waitMotionOnset(self, speed_ref=0, period=0.1, max_attempts=50):
        """
        Waits for the motion onset.

        Args:
            speed_ref (float): Reference speed to detect motion onset.
            period (float): Period to check the motion status.
            max_attempts (int): Maximum number of attempts to check the motion status.

        Returns:
            bool: True if the motion onset is detected, False otherwise.
        """
        self.__logger__.info("""Waiting for gaze motion onset STARTED!
                                 speed_ref=%s""" % str(speed_ref))
        q = yarp.Vector(6)
        for _ in range(0, max_attempts):
            self.IGazeControl.getJointsVelocities(q)
            v = []
            for i in range(0,6):
                v.append(q[i])
            speed = utils.norm(v)
            if speed > speed_ref:
                self.__logger__.info("""Motion onset DETECTED! speed_ref=%s""" % str(speed_ref))
                return True
            yarp.delay(period)
        self.__logger__.warning("""Motion onset TIMEOUT! speed_ref=%s""" % str(speed_ref))
        return False
