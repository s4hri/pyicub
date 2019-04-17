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
import threading

from Generics import GenericController

class PositionController(GenericController):

    def __init__(self, logger, driver, joints_list, iencoders):
        GenericController.__init__(self, logger)
        self.__IControlMode__ = driver.viewIControlMode()
        self.__IEncoders__ = iencoders
        self.__joints_list__ = joints_list
        self.setPositionControlMode(self.__joints_list__)
        self.__IPositionControl__ = driver.viewIPositionControl()

    def __waitMotionDone__(self, timeout):
        time.sleep(timeout)

    def getIPositionControl(self):
        return self.__IPositionControl__

    def getIEncoders(self):
        return self.__IEncoders__

    @GenericController.__atomicDecorator__
    def move(self, target_joints, req_time, joints_list=None, waitMotionDone=False):
        if joints_list is None:
            joints_list = self.__joints_list__
        disp = [0]*len(joints_list)
        speed_head = [0]*len(joints_list)
        tmp = yarp.Vector(len(joints_list))
        encs=yarp.Vector(16)
        while not self.__IEncoders__.getEncoders(encs.data()):
            self.__logger__.warning("Data from encoders not available!")
            time.sleep(0.1)
        i = 0
        for j in joints_list:
            tmp.set(i, target_joints[i])
            disp[i] = target_joints[i] - encs[j]
            if disp[i] < 0.0:
                disp[i] =- disp[i]
            speed_head[i] = disp[i]/req_time
            self.__IPositionControl__.setRefSpeed(j, speed_head[i])
            self.__IPositionControl__.positionMove(j, tmp[i])
            i+=1
        if waitMotionDone is True:
            self.__waitMotionDone__(timeout=req_time)

    @GenericController.__atomicDecorator__
    def setPositionControlMode(self, joints_list):
        for joint in joints_list:
            self.__IControlMode__.setControlMode(joint, yarp.VOCAB_CM_POSITION)
