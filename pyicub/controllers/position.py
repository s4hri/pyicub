"""
Module: position.py

This module defines the structure and control of iCub robot parts, their joints,
and a position controller for movement execution. It provides classes to define
iCub robot components, manage joint poses, and control robot movements through
the YARP interface.
"""

try:
    import yarp
except ImportError:
    pass

import os
import time
import json
import pyicub.utils as utils

DEFAULT_TIMEOUT = 30.0

class ICUB_PARTS:
    """
    Enumeration of iCub robot parts.
    """
    HEAD = 'head'
    FACE = 'face'
    TORSO = 'torso'
    LEFT_ARM = 'left_arm'
    RIGHT_ARM = 'right_arm'
    LEFT_LEG = 'left_leg'
    RIGHT_LEG = 'right_leg'

class iCubPart:
    """
    Represents an individual iCub robot part with its joint configuration.

    Attributes:
        name (str): Name of the robot part.
        robot_part (str): Corresponding robot section (head, torso, etc.).
        joints_nr (int): Number of joints in the part.
        joints_list (list[int]): List of joint indices.
        joints_speed (list[int]): List of speeds for each joint.
    """
    def __init__(self, name: str, robot_part: str, joints_nr: int, joints_list: list, joints_speed: list):
        """
        Initializes an iCub robot part.

        Args:
            name (str): The name of the part.
            robot_part (str): The section of the robot the part belongs to.
            joints_nr (int): Number of joints in the part.
            joints_list (list[int]): List of joint indices.
            joints_speed (list[int]): List of speeds for each joint.
        """
        self.name = name
        self.robot_part = robot_part
        self.joints_nr = joints_nr
        self.joints_list = joints_list
        self.joints_speed = joints_speed

    def toJSON(self) -> str:
        """
        Converts the iCub part object to a JSON string.

        Returns:
            str: JSON representation of the object.
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

# Define iCub parts with specific joints and speeds
ICUB_HEAD = iCubPart('HEAD', ICUB_PARTS.HEAD, 6, [0, 1, 2, 3, 4, 5], [10, 10, 20, 20, 20, 20])
ICUB_TORSO = iCubPart('TORSO', ICUB_PARTS.TORSO, 3, [0, 1, 2], [10, 10, 10])

class JointPose:
    """
    Represents a target pose for robot joints.
    
    Attributes:
        target_joints (list[float]): Desired joint positions.
        joints_list (list[int] or None): Specific joints to be controlled.
    """
    def __init__(self, target_joints: list[float], joints_list: list[int] = None):
        """
        Initializes a joint pose.

        Args:
            target_joints (list[float]): Target positions for the joints.
            joints_list (list[int], optional): List of specific joints to move. Defaults to None.
        """
        self.target_joints = target_joints
        self.joints_list = joints_list
    
    def toJSON(self) -> dict:
        """
        Converts the JointPose object to a dictionary.

        Returns:
            dict: Dictionary representation of the object.
        """
        return self.__dict__

class RemoteControlboard:
    """
    Interface for controlling an iCub robot part remotely using YARP.
    """
    def __init__(self, robot_name: str, part: iCubPart):
        """
        Initializes the remote control board.

        Args:
            robot_name (str): Name of the robot.
            part (iCubPart): The robot part to be controlled.
        """
        self.__robot_name__ = robot_name
        self.__part__ = part
        self.__pid__ = str(os.getpid())
        self.__driver__ = None
        props = self._getRobotPartProperties_()
        self.__driver__ = yarp.PolyDriver(props)

    def __del__(self):
        """
        Closes the YARP driver upon object deletion.
        """
        self.__driver__.close()
    
    def _getRobotPartProperties_(self) -> yarp.Property:
        """
        Defines and returns YARP properties for the robot part.

        Returns:
            yarp.Property: YARP properties for the remote control board.
        """
        props = yarp.Property()
        props.put("device", "remote_controlboard")
        props.put("local", f"/pyicub/{self.__pid__}/{self.__robot_name__}/{self.__part__.name}")
        props.put("remote", f"/{self.__robot_name__}/{self.__part__.robot_part}")
        return props
    
    def getDriver(self) -> yarp.PolyDriver:
        """
        Returns the YARP driver instance.

        Returns:
            yarp.PolyDriver: YARP driver instance.
        """
        return self.__driver__

class PositionController:
    """
    Controls joint movement of a robot part.
    """
    WAITMOTIONDONE_PERIOD = 0.1
    MOTION_COMPLETE_AT = 0.90

    def __init__(self, robot_name: str, part: iCubPart, logger):
        """
        Initializes the position controller.

        Args:
            robot_name (str): The name of the robot.
            part (iCubPart): The part to be controlled.
            logger: Logger instance for debugging.
        """
        self.__part__ = part
        self.__logger__ = logger
        self.__driver__ = RemoteControlboard(robot_name, part)
        self.__IPositionControl__ = None
        self.__joints__ = None
        self.__waitMotionDone__ = self.waitMotionDone

    def init(self):
        """
        Initializes the control interfaces.
        """
        self.__IPositionControl__ = self.PolyDriver.viewIPositionControl()
        self.__joints__ = self.__IPositionControl__.getAxes()
    
    @property
    def PolyDriver(self) -> yarp.PolyDriver:
        """
        Returns the PolyDriver instance.

        Returns:
            yarp.PolyDriver: PolyDriver instance controlling the robot part.
        """
        return self.__driver__.getDriver()
    
    def move(self, pose: JointPose):
        """
        Moves the joints to the specified target pose.

        Args:
            pose (JointPose): Target pose for the joints.
        """
        self.__IPositionControl__.positionMove(pose.target_joints)
    
    def waitMotionDone(self, timeout: float = DEFAULT_TIMEOUT) -> bool:
        """
        Waits until the movement is complete or times out.

        Args:
            timeout (float, optional): Maximum time to wait. Defaults to DEFAULT_TIMEOUT.

        Returns:
            bool: True if motion is completed, False otherwise.
        """
        return self.__IPositionControl__.checkMotionDone()
