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
import time as tt

class PositionController:

    def __init__(self, yarp_driver, joints_list, iencoders):
        self.__IControlMode__ = yarp_driver.viewIControlMode()
        self.__IEncoders__ = iencoders
        self.__joints_list__ = joints_list
        for joint in self.__joints_list__:
            self.__IControlMode__.setControlMode(joint, yarp.VOCAB_CM_POSITION)
        self.__IPositionControl__ = yarp_driver.viewIPositionControl()

    def getIPositionControl(self):
        return self.__IPositionControl__

    def getIEncoders(self):
        return self.__IEncoders__

    def move(self, target_joints, req_time, joints_list=None, waitMotionDone=False):
        if joints_list is None:
            joints_list = self.__joints_list__
        disp = [0]*len(joints_list)
        speed_head = [0]*len(joints_list)
        tmp = yarp.Vector(len(joints_list))
        encs=yarp.Vector(16)
        while not self.__IEncoders__.getEncoders(encs.data()):
            tt.sleep(0.1)
        i = 0
        for j in joints_list:
            tmp.set(i, target_joints[i])
            disp[i] = target_joints[i] - encs[j]
            if disp[i]<0.0:
                disp[i]=-disp[i]
            speed_head[i] = disp[i]/req_time
            self.__IPositionControl__.setRefSpeed(j, speed_head[i])
            self.__IPositionControl__.positionMove(j, tmp[i])
            i+=1
        if waitMotionDone is True:
            self.waitMotionDone(req_time)

    def waitMotionDone(self, req_time):
        tt.sleep(req_time)
