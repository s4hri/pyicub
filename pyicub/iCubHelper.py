#   Copyright (C) 2021  Davide De Tommaso
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

from pyicub.classes.Logger import YarpLogger
from pyicub.controllers.Generics import GenericController
from pyicub.controllers.GazeController import GazeController
from pyicub.controllers.PositionController import PositionController
from pyicub.modules.emotions import emotionsPyCtrl
from pyicub.modules.speech import speechPyCtrl
from pyicub.modules.face import facePyCtrl

import threading
import time
from collections import deque
from pyicub.classes.BufferedPort import BufferedReadPort

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
    FACE = iCubPart("face", 1)
    LEFT_ARM = iCubPart("left_arm", 16)
    RIGHT_ARM = iCubPart("right_arm", 16)
    TORSO = iCubPart("torso", 3)
    LEFT_LEG = iCubPart("left_leg", 6)
    RIGHT_LEG = iCubPart("right_leg", 6)


class iCubWatcher:
    def __init__(self, yarp_src_port, activate_function, callback, period=0.01, autostart=False):
        self._port = BufferedReadPort(yarp_src_port + "_reader_" + str(id(self)), yarp_src_port,)
        self._activate = activate_function
        self._callback = callback
        self._period = period
        self._values = deque( int(1000/(period*1000))*[None], maxlen=int(1000/(period*1000))) #Values of the last second
        self._stop_thread = False
        if autostart:
            self.start()

    def start(self):
        if self._stop_thread:
           self.stop()
        self._worker_thread = threading.Thread(target=self.worker)
        self._worker_thread.start()

    def stop(self):
        if not self._stop_thread:
            self._stop_thread = True
        self._worker_thread.join()
        self._stop_thread = False

    def worker(self):
        while not self._stop_thread:
            res = self._port.read(shouldWait=False)
            if not res is None:
                self._values.append(res.toString())
                if self._activate(self._values):
                    self._callback()
            time.sleep(self._period)

    def __del__(self):
        self.stop()
        del self._port

class iCub:
    def __init__(self, robot, logtype=YarpLogger.DEBUG):
        self.__robot__ = robot
        self.__position_controllers__ = {}
        self.__drivers__ = {}
        self.__encoders__ = {}
        self.__gaze_controller__ = None
        self.__gaze__ = None
        self.__emo__ = None
        self.__speech__ = None
        self.__face__ = None
        self.__logger__ = YarpLogger(logtype=logtype)
        self.__watchdogs__ = []

    def __getDriver__(self, robot_part):
        if not robot_part.name in self.__drivers__.keys():
            props = self.__getRobotPartProperties__(robot_part)
            self.__drivers__[robot_part.name] = yarp.PolyDriver(props)
        return self.__drivers__[robot_part.name]

    def __getIEncoders__(self, robot_part):
        if not robot_part.name in self.__encoders__.keys():
            driver = self.__getDriver__(robot_part)
            self.__encoders__[robot_part.name] = driver.viewIEncoders()
        return self.__encoders__[robot_part.name]

    def __getRobotPartProperties__(self, robot_part):
        props = yarp.Property()
        props.put("device","remote_controlboard")
        props.put("local","/client/" + self.__robot__ + "/" + robot_part.name)
        props.put("remote","/" + self.__robot__ + "/" + robot_part.name)
        return props

    @property
    def gaze(self):
        if self.__gaze__ is None:
            self.__gaze__ = GazeController(self.__robot__, self.__logger__)
        return self.__gaze__

    @property
    def emo(self):
        if self.__emo__ is None:
            self.__emo__ = emotionsPyCtrl(self.__robot__)
        return self.__emo__

    @property
    def speech(self):
        if self.__speech__ is None:
            self.__speech__ = speechPyCtrl(self.__robot__)
        return self.__speech__

    @property
    def face(self):
        if self.__face__ is None:
            self.__face__ = facePyCtrl(self.__robot__)
        return self.__face__

    def getPositionController(self, robot_part, joints_list=None):
        if not robot_part in self.__position_controllers__.keys():
            driver = self.__getDriver__(robot_part)
            iencoders = self.__getIEncoders__(robot_part)
            if joints_list is None:
                joints_list = robot_part.joints_list
            self.__position_controllers__[robot_part.name] = PositionController(self.__logger__, driver, joints_list, iencoders)
        return self.__position_controllers__[robot_part.name]
