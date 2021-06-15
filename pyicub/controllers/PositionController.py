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
import time
import pyicub.utils as utils

from pyicub.core.Logger import YarpLogger

class PositionController:

    MIN_JOINTS_DIST = 1
    WAITMOTIONDONE_PERIOD = 0.01

    def __init__(self, driver, joints_list, iencoders):
        self.__logger__ = YarpLogger.getLogger()
        self.__IControlMode__ = driver.viewIControlMode()
        self.__IEncoders__ = iencoders
        self.__joints_list__ = joints_list
        self.__setPositionControlMode__(self.__joints_list__)
        self.__IPositionControl__ = driver.viewIPositionControl()

    def __setPositionControlMode__(self, joints_list):
        for joint in joints_list:
            self.__IControlMode__.setControlMode(joint, yarp.VOCAB_CM_POSITION)

    def __waitMotionDone__(self, target_joints, joints_list):
        encs=yarp.Vector(16)
        while True:
            while not self.__IEncoders__.getEncoders(encs.data()):
                yarp.delay(0.005)
            v = []
            for j in joints_list:
                v.append(encs[j])
            dist = utils.vector_distance(v, target_joints)
            if dist < PositionController.MIN_JOINTS_DIST:
                break
            yarp.delay(PositionController.WAITMOTIONDONE_PERIOD)

    def getIPositionControl(self):
        return self.__IPositionControl__

    def getIEncoders(self):
        return self.__IEncoders__

    def move(self, target_joints, req_time, joints_list=None, waitMotionDone=True):
        self.__logger__.debug("""Moving joints STARTED!
                              target_joints:%s
                              req_time:%.2f,
                              joints_list=%s,
                              waitMotionDone=%s""" %
                              (str(target_joints),
                              req_time,
                              str(joints_list),
                              str(waitMotionDone)) )
        if joints_list is None:
            joints_list = self.__joints_list__
        disp = [0]*len(joints_list)
        speed = [0]*len(joints_list)
        tmp = yarp.Vector(len(joints_list))
        encs=yarp.Vector(16)
        while not self.__IEncoders__.getEncoders(encs.data()):
            yarp.delay(0.005)
        i = 0
        for j in joints_list:
            tmp.set(i, target_joints[i])
            disp[i] = target_joints[i] - encs[j]
            if disp[i] < 0.0:
                disp[i] =- disp[i]
            speed[i] = disp[i]/req_time
            self.__IPositionControl__.setRefSpeed(j, speed[i])
            self.__IPositionControl__.positionMove(j, tmp[i])
            i+=1
        if waitMotionDone is True:
            self.__waitMotionDone__(target_joints, joints_list)
        self.__logger__.debug("""Moving joints COMPLETED!
                              target_joints:%s
                              req_time:%.2f,
                              joints_list=%s,
                              waitMotionDone=%s""" %
                              (str(target_joints),
                              req_time,
                              str(joints_list),
                              str(waitMotionDone)) )

    def moveRefVel(self, req_time, target_joints, joints_list=None, vel_list=None, waitMotionDone=True):
        self.__logger__.debug("""Moving joints in position control STARTED!
                              target_joints:%s
                              req_time:%.2f,
                              vel_list=%s,
                              waitMotionDone=%s""" %
                              str(target_joints),
                              req_time,
                              str(vel_list),
                              str(waitMotionDone))

        if joints_list is None:
            joints_list = self.__joints_list__
        jl = yarp.Vector(len(joints_list))
        vl = yarp.Vector(len(vel_list))
        i = 0
        for j in joints_list:
            jl.set(i, target_joints[i])
            vl.set(i, vel_list[i])
            self.__IPositionControl__.setRefSpeed(j, vl[i])
            self.__IPositionControl__.positionMove(j, jl[i])
            i+=1
        if waitMotionDone is True:
            self.__waitMotionDone__(target_joints, joints_list)
        self.__logger__.debug("""Moving joints COMPLETED!
                              target_joints:%s
                              req_time:%.2f,
                              vel_list=%s,
                              waitMotionDone=%s""" %
                              str(target_joints),
                              req_time,
                              str(vel_list),
                              str(waitMotionDone))
