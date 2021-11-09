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
        self._target_joints_ = target_joints
        self._joints_list_ = joints_list

    @property
    def target_joints(self):
        return self._target_joints_

    @property
    def joints_list(self):
        return self._joints_list_

class JointPoseVel:

    def __init__(self, target_position, vel_list, joints_list=None):
        self._target_position_ = target_position
        self._vel_list_ = vel_list
        self._joints_list_ = joints_list

    @property
    def joints_list(self):
        return self._joints_list_

    @property
    def target_position(self):
        return self._target_position_

    @property
    def vel_list(self):
        return self._vel_list_

class JointsTrajectoryCheckpoint:

    def __init__(self, pose: JointPose, duration: float):
        self._pose_ = pose
        self._duration_ = duration

    @property
    def pose(self):
        return self._pose_

    @property
    def duration(self):
        return self._duration_


class LimbMotion:
    def __init__(self, part_name: iCubPart):
        self._part_name_ = part_name
        self._checkpoints_ = []

    @property
    def durations(self):
        return self._durations_

    @property
    def part_name(self):
        return self._part_name_

    @property
    def checkpoints(self):
        return self._checkpoints_

    def addCheckpoint(self, checkpoint: JointsTrajectoryCheckpoint):
        self._checkpoints_.append(checkpoint)

class PositionController:

    MIN_JOINTS_DIST = 1
    WAITMOTIONDONE_PERIOD = 0.01

    def __init__(self, driver, joints_list, iencoders, logger=YarpLogger.getLogger()):
        self.__logger__ = logger
        self.__IControlMode__ = driver.viewIControlMode()
        self.__IEncoders__ = iencoders
        self.__joints_list__ = joints_list
        self.__setPositionControlMode__(self.__joints_list__)
        self.__IPositionControl__ = driver.viewIPositionControl()

    def __setPositionControlMode__(self, joints_list):
        for joint in joints_list:
            self.__IControlMode__.setControlMode(joint, yarp.VOCAB_CM_POSITION)

    def getIPositionControl(self):
        return self.__IPositionControl__

    def getIEncoders(self):
        return self.__IEncoders__

    def move(self, pose: JointPose, req_time: float, waitMotionDone: bool=True):
        target_joints = pose.target_joints
        joints_list = pose.joints_list
        self.__logger__.info("""Moving joints STARTED!
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
            self.waitMotionDone(JointPose(target_joints, joints_list), timeout=2*req_time)
        self.__logger__.info("""Moving joints COMPLETED!
                              target_joints:%s
                              req_time:%.2f,
                              joints_list=%s,
                              waitMotionDone=%s""" %
                              (str(target_joints),
                              req_time,
                              str(joints_list),
                              str(waitMotionDone)) )


    def moveRefVel(self, pose: JointPoseVel, req_time: float, waitMotionDone: bool=True):
        target_joints = pose.target_joints
        vel_list = pose.vel_list
        joints_list = pose.joints_list

        self.__logger__.info("""Moving joints in position control STARTED!
                              target_joints:%s
                              req_time:%.2f,
                              vel_list=%s,
                              waitMotionDone=%s""" %
                              (str(target_joints),
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
        self.__logger__.debug("""Moving joints COMPLETED!
                              target_joints:%s
                              req_time:%.2f,
                              vel_list=%s,
                              waitMotionDone=%s""" %
                              (str(target_joints),
                              req_time,
                              str(vel_list),
                              str(waitMotionDone)) )

    def waitMotionDone(self, pose: JointPose, timeout: float):
        target_joints = pose.target_joints
        joints_list = pose.joints_list
        self.__logger__.info("""Waiting for motion done STARTED!""")
        encs=yarp.Vector(16)
        max_attempts = int(timeout/PositionController.WAITMOTIONDONE_PERIOD)
        for _ in range(0, max_attempts):
            while not self.__IEncoders__.getEncoders(encs.data()):
                yarp.delay(0.05)
            v = []
            for j in joints_list:
                v.append(encs[j])
            dist = utils.vector_distance(v, target_joints)
            if dist < PositionController.MIN_JOINTS_DIST:
                self.__logger__.info("""Motion done DETECTED!""")
                return True
            yarp.delay(PositionController.WAITMOTIONDONE_PERIOD)
        self.__logger__.warning("""Motion done TIMEOUT!""")
        return False
