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
Module: gaze.py

This module provides a GazeController class to manage the gaze control of a robot using YARP.
It includes functionalities to control gaze direction, block and clear eye and neck movements, 
and set parameters for gaze control.
"""

import os
import yarp
import pyicub.utils as utils

class GazeControllerPolyDriver:
    """
    Manages the YARP PolyDriver for the gaze controller.

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
        self.__pid__ = str(os.getpid())
        self.__props__ = yarp.Property()
        self.__props__.put("robot", robot)
        self.__props__.put("device","gazecontrollerclient")
        self.__props__.put("local","/pyicub/gaze/" + self.__pid__)
        self.__props__.put("remote","/iKinGazeCtrl")
        self.__driver__ = yarp.PolyDriver(self.__props__)

    def __del__(self):
        """
        Destructor to close the YARP PolyDriver.
        """
        self.__driver__.close()

    @property
    def properties(self):
        """
        Returns the properties of the YARP PolyDriver.

        Returns:
            yarp.Property: The properties of the YARP PolyDriver.
        """
        return self.__props__

    def getDriver(self):
        """
        Returns the YARP PolyDriver instance.

        Returns:
            yarp.PolyDriver: The YARP PolyDriver instance.
        """
        return self.__driver__

class GazeController:
    """
    Manages the gaze control of a robot using YARP.

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
        Returns:
            yarp.PolyDriver: The YARP PolyDriver instance.
        """
        return self.__driver__.getDriver()

    @property
    def IGazeControl(self):
        """
        Returns:
            IGazeControl: The gaze control interface.
        """
        return self.__IGazeControl__
    
    def __lookAtAbsAngles__(self, angles, waitMotionDone=True, timeout=0.0):
        """
        Direct the gaze to specific absolute angles.

        This method commands the gaze controller to look at the specified absolute angles.
        Optionally, it can wait until the motion is completed or a timeout occurs.

        :param angles: A list of three angles [azimuth, elevation, vergence] to look at.
        :type angles: list of float
        :param waitMotionDone: If True, the method waits until the motion is completed. Default is True.
        :type waitMotionDone: bool, optional
        :param timeout: The maximum time to wait for the motion to complete. Default is 0.0.
        :type timeout: float, optional
        :return: None
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
        Directs the gaze to look at relative angles.

        This method commands the gaze controller to look at the specified relative angles.
        Optionally, it can wait for the motion to complete within a given timeout.

        :param angles: A list of three angles [azimuth, elevation, vergence] to look at.
        :type angles: list of float
        :param waitMotionDone: If True, the method waits for the motion to complete before returning.
        :type waitMotionDone: bool, optional
        :param timeout: The maximum time to wait for the motion to complete, in seconds.
        :type timeout: float, optional
        :return: None
        :rtype: None
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
        Commands the gaze controller to look at the specified absolute angles.

        :param azi: Azimuth angle in degrees.
        :type azi: float
        :param ele: Elevation angle in degrees.
        :type ele: float
        :param ver: Vergence angle in degrees.
        :type ver: float
        :param waitMotionDone: If True, the method will wait until the motion is completed.
        :type waitMotionDone: bool, optional
        :param timeout: Maximum time to wait for the motion to complete, in seconds. A value of 0.0 means no timeout.
        :type timeout: float, optional
        """
        angles = yarp.Vector(3)
        angles.set(0, azi)
        angles.set(1, ele)
        angles.set(2, ver)
        self.__lookAtAbsAngles__(angles, waitMotionDone, timeout)

    def lookAtRelAngles(self, azi, ele, ver, waitMotionDone=True, timeout=0.0):
        """
        Directs the gaze to the specified relative angles.

        Parameters
        ----------
        azi : float
            The azimuth angle in degrees.
        ele : float
            The elevation angle in degrees.
        ver : float
            The vergence angle in degrees.
        waitMotionDone : bool, optional
            If True, the method waits until the motion is completed (default is True).
        timeout : float, optional
            The maximum time to wait for the motion to complete in seconds (default is 0.0, which means no timeout).

        Returns
        -------
        None
        """
        angles = yarp.Vector(3)
        angles.set(0, azi)
        angles.set(1, ele)
        angles.set(2, ver)
        self.__lookAtRelAngles__(angles, waitMotionDone, timeout)

    def lookAtFixationPoint(self, x, y, z, waitMotionDone=True, timeout=0.0):
        """
        Directs the gaze to a specified fixation point in 3D space.

        Parameters
        ----------
        x : float
            The x-coordinate of the fixation point.
        y : float
            The y-coordinate of the fixation point.
        z : float
            The z-coordinate of the fixation point.
        waitMotionDone : bool, optional
            If True, the method waits until the motion is completed (default is True).
        timeout : float, optional
            The maximum time to wait for the motion to complete in seconds (default is 0.0).

        Returns
        -------
        None
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
        Reset the gaze controller by clearing the eyes and neck positions.

        This method calls `clearEyes` to reset the eye positions and `clearNeck` to reset the neck positions.
        """
        self.clearEyes()
        self.clearNeck()

    def setParams(self, neck_tt, eyes_tt):
        """
        Args:
            neck_tt (float): Trajectory time for the neck.
            eyes_tt (float): Trajectory time for the eyes.
        """
        self.IGazeControl.setNeckTrajTime(neck_tt)
        self.IGazeControl.setEyesTrajTime(eyes_tt)

    def setTrackingMode(self, mode):
        """
        Args:
            mode (bool): True to enable tracking mode, False to disable.
        """
        self.IGazeControl.setTrackingMode(mode)

    def waitMotionDone(self, period=0.1, timeout=0.0):
        """
        Args:
            period (float): Period to check the motion status.
            timeout (float): Timeout for waiting for the motion to complete.

        Returns:
            bool: True if the motion completed, False otherwise.
        """
        return self.IGazeControl.waitMotionDone(period=period, timeout=timeout)

    def waitMotionOnset(self, speed_ref=0, period=0.1, max_attempts=50):
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