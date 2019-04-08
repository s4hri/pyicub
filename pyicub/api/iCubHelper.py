#   Copyright (C) 2019  Davide De Tommaso
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>

import yarp
import time
from pyicub.api.yarp_classes.GazeController import GazeController
from pyicub.api.yarp_classes.PositionController import PositionController
from pyicub.api.yarp_modules.emotions import emotionsPyCtrl
from pyicub.api.yarp_modules.speech import speechPyCtrl
from pyicub.api import iGazeHelper

class iCubPart:
    def __init__(self, name, joints_n):
        self.name = name
        self.joints_n = joints_n
        self.joints_list = range(0, joints_n)

class ROBOT_TYPE:
    ICUB = "icub"
    ICUB_SIMULATOR = "icubSim"

class ICUB_PARTS:
    HEAD = iCubPart("head", 6)
    LEFT_ARM = iCubPart("left_arm", 16)
    RIGHT_ARM = iCubPart("right_arm", 16)
    TORSO = iCubPart("torso", 3)
    LEFT_LEG = iCubPart("left_leg", 6)
    RIGHT_LEG = iCubPart("right_leg", 6)

class iCub:

    def __init__(self, robot):
        self.__robot__ = robot
        self.__position_controllers__ = {}
        self.__drivers__ = {}
        self.__encoders__ = {}
        self.__gaze_controller__ = None
        self.__gaze__ = None
        self.__emo__ = None
        self.__speech__ = None

    @property
    def gaze(self):
        if self.__gaze__ is None:
            ctrl = self.getIGazeControl()
            self.__gaze__ = iGazeHelper.iGazeHelper(ctrl)
        return self.__gaze__

    @property
    def emo(self):
        if self.__emo__ is None:
            self.__emo__ = emotionsPyCtrl()
        return self.__emo__

    @property
    def speech(self):
        if self.__speech__ is None:
            self.__speech__ = speechPyCtrl()
        return self.__speech__

    def getDriver(self, robot_part):
        if not robot_part.name in self.__drivers__.keys():
            props = self.getRobotPartProperties(robot_part)
            self.__drivers__[robot_part.name] = yarp.PolyDriver(props)
        return self.__drivers__[robot_part.name]

    def getIEncoders(self, robot_part):
        if not robot_part.name in self.__encoders__.keys():
            driver = self.getDriver(robot_part)
            self.__encoders__[robot_part.name] = driver.viewIEncoders()
        return self.__encoders__[robot_part.name]

    def getIGazeControl(self):
        if self.__gaze_controller__ is None:
            self.__gaze_controller__ = GazeController()
        return self.__gaze_controller__.getIGazeControl()

    def getIPositionControl(self, robot_part, joints_list):
        if not robot_part.name in self.__position_controllers__.keys():
            driver = self.getDriver(robot_part)
            if joints_list is None:
                joints_list = robot_part.joints_list
            iencoders = self.getIEncoders(robot_part)
            self.__position_controllers__[robot_part.name] = PositionController(driver, joints_list, iencoders)
        return self.__position_controllers__[robot_part.name].getIPositionControl()

    def getRobotPartProperties(self, robot_part):
        props = yarp.Property()
        props.put("device","remote_controlboard")
        props.put("local","/client/" + robot_part.name)
        props.put("remote","/" + self.__robot__ + "/" + robot_part.name)
        return props

    def getPositionController(self, robot_part):
        if not robot_part in self.__position_controllers__.keys():
            self.getIPositionControl(robot_part, robot_part.joints_list)
        return self.__position_controllers__[robot_part.name]
