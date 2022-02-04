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
import pyicub.utils as utils

from pyicub.core.logger import YarpLogger

class ICUB_PARTS:
    HEAD       = 'head'
    FACE       = 'face'
    TORSO      = 'torso'
    LEFT_ARM   = 'left_arm'
    RIGHT_ARM  = 'right_arm'
    LEFT_LEG   = 'left_leg'
    RIGHT_LEG  = 'right_leg'

class iCubPart:
    def __init__(self, name, joints_n):
        self.name = name
        self.joints_n = joints_n
        self.joints_list = range(0, joints_n)

class JointPose:

    def __init__(self, target_joints, joints_list=None):
        self.target_joints = target_joints
        self.joints_list = joints_list


class JointPoseVel:

    def __init__(self, target_position, vel_list, joints_list=None):
        self.target_position = target_position
        self.vel_list = vel_list
        self.joints_list = joints_list

class JointsTrajectoryCheckpoint:
    DEFAULT_TIMEOUT = 10.0

    def __init__(self, pose: JointPose, duration: float, timeout: float=DEFAULT_TIMEOUT):
        self.pose = pose
        self.duration = duration
        self.timeout = timeout

class LimbMotion:
    def __init__(self, part_name: iCubPart):
        self.part_name = part_name
        self.checkpoints = []

    def addCheckpoint(self, checkpoint: JointsTrajectoryCheckpoint):
        self.checkpoints.append(checkpoint)


class PositionController:

    WAITMOTIONDONE_PERIOD = 0.01

    def __init__(self, driver, joints_list, iencoders, logger=YarpLogger.getLogger()):
        self.__logger__ = logger
        self.__IControlMode__ = driver.viewIControlMode()
        self.__IEncoders__ = iencoders
        self.__joints_list__ = joints_list
        self.__setPositionControlMode__(self.__joints_list__)
        self.__IPositionControl__ = driver.viewIPositionControl()
        self.__mot_id__ = 0

    def __setPositionControlMode__(self, joints_list):
        for joint in joints_list:
            self.__IControlMode__.setControlMode(joint, yarp.VOCAB_CM_POSITION)

    def getIPositionControl(self):
        return self.__IPositionControl__

    def getIEncoders(self):
        return self.__IEncoders__

    def move(self, pose: JointPose, req_time: float, timeout: float, waitMotionDone: bool=True):
        self.__mot_id__ += 1
        target_joints = pose.target_joints
        joints_list = pose.joints_list
        self.__logger__.info("""Motion <%d> STARTED!
                              target_joints:%s
                              req_time:%.2f,
                              joints_list=%s,
                              waitMotionDone=%s""" %
                              (self.__mot_id__,
                              str(target_joints),
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
            res = self.waitMotionDone(timeout=timeout)
            if res:
                self.__logger__.info("""Motion <%d> COMPLETED!
                                    target_joints:%s
                                    req_time:%.2f,
                                    joints_list=%s,
                                    waitMotionDone=%s""" %
                                    (self.__mot_id__,
                                    str(target_joints),
                                    req_time,
                                    str(joints_list),
                                    str(waitMotionDone)) )
            else:
                self.__logger__.warning("""Motion <%d> TIMEOUT!
                                    target_joints:%s
                                    joints_list=%s""" %
                                    (self.__mot_id__,
                                    str(target_joints),
                                    str(joints_list)) )



    def moveRefVel(self, pose: JointPoseVel, req_time: float, waitMotionDone: bool=True):
        target_joints = pose.target_joints
        vel_list = pose.vel_list
        joints_list = pose.joints_list

        self.__logger__.info("""Motion <%d> STARTED!
                              target_joints:%s
                              req_time:%.2f,
                              vel_list=%s,
                              waitMotionDone=%s""" %
                              (self.__mot_id__,
                              str(target_joints),
                              req_time,
                              str(vel_list),
                              str(waitMotionDone)) )

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
            self.waitMotionDone(target_joints, joints_list, timeout=2*req_time)
        self.__logger__.debug("""Motion <%d> COMPLETED!
                              target_joints:%s
                              req_time:%.2f,
                              vel_list=%s,
                              waitMotionDone=%s""" %
                              (self.__mot_id__,
                              str(target_joints),
                              req_time,
                              str(vel_list),
                              str(waitMotionDone)) )

    def waitMotionDone(self, timeout: float):
        max_attempts = int(timeout/PositionController.WAITMOTIONDONE_PERIOD)
        for _ in range(0, max_attempts):
            if self.__IPositionControl__.checkMotionDone():
                return True
            yarp.delay(PositionController.WAITMOTIONDONE_PERIOD)
        return False
