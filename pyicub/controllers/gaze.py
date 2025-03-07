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

    def __init__(self, robot: str):
        """
        Initializes the GazeControllerPolyDriver with the given robot name.

        Args:
            robot (str): The name of the robot.
        """
        self.__pid__ = str(os.getpid())
        self.__props__ = yarp.Property()
        self.__props__.put("robot", robot)
        self.__props__.put("device", "gazecontrollerclient")
        self.__props__.put("local", f"/pyicub/gaze/{self.__pid__}")
        self.__props__.put("remote", "/iKinGazeCtrl")
        self.__driver__ = yarp.PolyDriver(self.__props__)

    def __del__(self):
        """
        Destructor to close the YARP PolyDriver.
        """
        self.__driver__.close()

    @property
    def properties(self) -> yarp.Property:
        """
        Returns the properties of the YARP PolyDriver.

        Returns:
            yarp.Property: The properties of the YARP PolyDriver.
        """
        return self.__props__

    def getDriver(self) -> yarp.PolyDriver:
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

    def __init__(self, robot: str, logger):
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

    def isValid(self) -> bool:
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
    def PolyDriver(self) -> yarp.PolyDriver:
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

    def blockEyes(self, vergence: float):
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

    def setParams(self, neck_tt: float, eyes_tt: float):
        """
        Sets the trajectory times for the neck and eyes.

        Args:
            neck_tt (float): Trajectory time for the neck.
            eyes_tt (float): Trajectory time for the eyes.
        """
        self.IGazeControl.setNeckTrajTime(neck_tt)
        self.IGazeControl.setEyesTrajTime(eyes_tt)

    def setTrackingMode(self, mode: bool):
        """
        Sets the tracking mode.

        Args:
            mode (bool): True to enable tracking mode, False to disable.
        """
        self.IGazeControl.setTrackingMode(mode)

    def waitMotionDone(self, period: float = 0.1, timeout: float = 0.0) -> bool:
        """
        Waits for the motion to complete.

        Args:
            period (float): Period to check the motion status.
            timeout (float): Timeout for waiting for the motion to complete.

        Returns:
            bool: True if the motion completed, False otherwise.
        """
        return self.IGazeControl.waitMotionDone(period=period, timeout=timeout)
