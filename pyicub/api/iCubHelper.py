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

    def __init__(self, robot, gaze_controller=False, facial_expressions=False, speech=False):
        self.__robot__ = robot
        self.__position_controllers__ = {}
        self.__drivers__ = {}
        self.__encoders__ = {}
        self.__gaze_controller__ = None
        self.gaze = None
        self.emo = None
        self.speech = None
        if gaze_controller is True:
            self.getIGazeControl()
        if facial_expressions is True:
            self.emo = self.getEmotionsModule()
        if speech is True:
            self.speech = self.getSpeechModule()

    def getEmotionsModule(self):
        if self.emo is None:
            self.emo = emotionsPyCtrl()
        return self.emo

    def getDriver(self, robot_part):
        if not robot_part.name in self.__drivers__.keys():
            props = self.getRobotPartProperties(robot_part)
            self.__drivers__[robot_part.name] = yarp.PolyDriver(props)
        return self.__drivers__[robot_part.name]

    def getIEncoders(self, robot_part, driver=None):
        if not robot_part.name in self.__encoders__.keys():
            driver = self.getDriver(robot_part)
            self.__encoders__[robot_part.name] = driver.viewIEncoders()
        return self.__encoders__[robot_part.name]

    def getIGazeControl(self):
        if self.__gaze_controller__ is None:
            self.__gaze_controller__ = GazeController()
            self.gaze = iGazeHelper.iGazeHelper(self.__gaze_controller__)
        return self.__gaze_controller__.getIGazeControl()

    def getIPositionControl(self, robot_part, joints_list=None):
        if not robot_part.name in self.__position_controllers__.keys():
            driver = self.getDriver(robot_part)
            if joints_list is None:
                joints_list = range(0, robot_part.joints_n)
            self.__position_controllers__[robot_part.name] = PositionController(driver, joints_list)
        return self.__position_controllers__[robot_part.name].getIPositionControl()

    def getRobotPartProperties(self, robot_part):
        props = yarp.Property()
        props.put("device","remote_controlboard")
        props.put("local","/client/" + robot_part.name)
        props.put("remote","/" + self.__robot__ + "/" + robot_part.name)
        return props

    def getSpeechModule(self):
        if self.speech is None:
            self.speech = speechPyCtrl()
        return self.speech

    def initController(self, robot_parts=[]):
        for part in robot_parts:
            self.getIPositionControl(part)
            self.getIEncoders(part)

    def move(self, robot_part, target_joints, req_time, joints_list):
        disp = [0]*len(joints_list)
        speed_head = [0]*len(joints_list)
        tmp = yarp.Vector(len(joints_list))
        encs=yarp.Vector(16)
        while not self.getIEncoders(robot_part).getEncoders(encs.data()):
            tt.sleep(0.1)
        i = 0
        for j in joints_list:
            tmp.set(i, target_joints[i])
            disp[i] = target_joints[i] - encs[j]
            if disp[i]<0.0:
                disp[i]=-disp[i]
            speed_head[i] = disp[i]/req_time

            self.getIPositionControl(robot_part, joints_list).setRefSpeed(j, speed_head[i])
            self.getIPositionControl(robot_part, joints_list).positionMove(j, tmp[i])
            i+=1

    def moveSync(self, robot_part, target_joints, req_time, joints_list):
        self.move(robot_part, target_joints, req_time, joints_list)
        time.sleep(req_time)
