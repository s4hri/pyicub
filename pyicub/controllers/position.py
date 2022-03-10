# BSD 2-Clause License
#
# Copyright (c) 2022, Social Cognition in Human-Robot Interaction,
#                     Istituto Italiano di Tecnologia, Genova
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import time
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

class JointsTrajectoryCheckpoint:

    def __init__(self, pose: JointPose, duration: float=0.0, timeout: float=0.0):
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

    WAITMOTIONDONE_PERIOD = 0.1
    MOTION_COMPLETE_AT = 0.9
    DEFAULT_TIMEOUT = 10.0

    def __init__(self, robot, robot_part, logger=YarpLogger.getLogger()):
        self.__pid__        = str(os.getpid())
        self.__logger__     = logger
        self.__robot__      = robot
        self.__robot_part__ = robot_part
        self.__driver__ = self._getDriver_()
        self.__IEncoders__        = self.__driver__.viewIEncoders()
        self.__IControlLimits__   = self.__driver__.viewIControlLimits()
        self.__IControlMode__     = self.__driver__.viewIControlMode()
        self.__IPositionControl__ = self.__driver__.viewIPositionControl()
        self.__joints__           = self.__IPositionControl__.getAxes()
        self.__setPositionControlMode__(self.__joints__)
        self.__mot_id__ = 0
        self.__waitMotionDone__ = self.waitMotionDone

    def _getRobotPartProperties_(self):
        props = yarp.Property()
        props.put("device","remote_controlboard")
        props.put("local","/client/" + self.__pid__ + "/" + self.__robot__ + "/" + self.__robot_part__.name)
        props.put("remote","/" + self.__robot__ + "/" + self.__robot_part__.name)
        return props

    def _getDriver_(self):
        props  = self._getRobotPartProperties_()
        driver = yarp.PolyDriver(props)
        if driver.isValid():
            return driver
        else:
            self.__logger__.warning("Driver not properly initialized props=%s" % str(props))
            return False

    def __setPositionControlMode__(self, joints):
        modes = yarp.IVector(joints, yarp.VOCAB_CM_POSITION)
        self.__IControlMode__.setControlModes(modes)

    def getIPositionControl(self):
        return self.__IPositionControl__

    def getIEncoders(self):
        return self.__IEncoders__

    def getIControlLimits(self):
        return self.__IControlLimits__

    def move(self, pose: JointPose, req_time: float=0.0, timeout: float=0.0, speed: float=10.0, waitMotionDone: bool=True):
        self.__mot_id__ += 1
        target_joints = pose.target_joints
        joints_list = pose.joints_list
        if timeout == 0.0:
            timeout = PositionController.DEFAULT_TIMEOUT
        self.__logger__.info("""Motion <%d> STARTED!
                                robot_part:%s,
                                target_joints:%s,
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s""" %
                                (
                                  self.__mot_id__         ,
                                  self.__robot_part__.name,
                                  str(target_joints)      ,
                                  req_time                ,
                                  str(joints_list)        ,
                                  str(waitMotionDone)     ,
                                  str(timeout)
                                )
                            )
        if joints_list is None:
            joints_list = range(0, self.__joints__)

        if req_time > 0.0:
            disp  = [0]*len(joints_list)
            speeds = [0]*len(joints_list)
            tmp   = yarp.Vector(self.__joints__)
            encs  = yarp.Vector(self.__joints__)
            while not self.__IEncoders__.getEncoders(encs.data()):
                yarp.delay(0.005)
            i = 0
            for j in joints_list:
                tmp.set(i, target_joints[i])
                disp[i] = target_joints[i] - encs[j]
                if disp[i] < 0.0:
                    disp[i] =- disp[i]
                speeds[i] = disp[i]/req_time
                self.__IPositionControl__.setRefSpeed(j, speeds[i])
                self.__IPositionControl__.positionMove(j, tmp[i])
                i+=1
        else:
            speeds = [0]*len(joints_list)
            tmp   = yarp.Vector(self.__joints__)
            i = 0
            for j in joints_list:
                tmp.set(i, target_joints[i])
                speeds[i] = speed
                self.__IPositionControl__.setRefSpeed(j, speeds[i])
                self.__IPositionControl__.positionMove(j, tmp[i])
                i+=1

        if waitMotionDone is True:
            res = self.__waitMotionDone__(timeout=timeout)
            if res:
                self.__logger__.info("""Motion <%d> COMPLETED!
                                robot_part:%s,
                                target_joints:%s
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s""" %
                                (
                                    self.__mot_id__         ,
                                    self.__robot_part__.name,
                                    str(target_joints)      ,
                                    req_time                ,
                                    str(joints_list)        ,
                                    str(waitMotionDone)     ,
                                    str(timeout)
                                ))
            else:
                self.__logger__.warning("""Motion <%d> TIMEOUT!
                                robot_part:%s,
                                target_joints:%s
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s""" %
                                (
                                    self.__mot_id__         ,
                                    self.__robot_part__.name,
                                    str(target_joints)      ,
                                    req_time                ,
                                    str(joints_list)        ,
                                    str(waitMotionDone)     ,
                                    str(timeout)
                                ))


    def setCustomWaitMotionDone(self, motion_complete_at=MOTION_COMPLETE_AT):
        self.__waitMotionDone__ = self.waitMotionDone2
        PositionController.MOTION_COMPLETE_AT = motion_complete_at

    def unsetCustomWaitMotionDone(self):
        self.__waitMotionDone__ = self.waitMotionDone

    def waitMotionDone(self, timeout: float):
        t0 = time.perf_counter()
        while (time.perf_counter() - t0) < timeout:
            if self.__IPositionControl__.checkMotionDone():
                return True
            yarp.delay(PositionController.WAITMOTIONDONE_PERIOD)
        return False

    def waitMotionDone2(self, timeout: float):
        t0 = time.perf_counter()
        target_pos = yarp.Vector(self.__joints__)
        encs=yarp.Vector(self.__joints__)
        self.__IPositionControl__.getTargetPositions(target_pos.data())
        count = 0
        while (time.perf_counter() - t0) < timeout:
            while not self.__IEncoders__.getEncoders(encs.data()):
                yarp.delay(0.05)
            v = []
            w = []
            for i in range(0, self.__joints__):
                v.append(encs[i])
                w.append(target_pos[i])
            if count == 0:
                tot_disp = utils.vector_distance(v, w)
            count+=1
            dist = utils.vector_distance(v, w)
            if dist <= (1.0 - PositionController.MOTION_COMPLETE_AT)*tot_disp:
                return True
            yarp.delay(PositionController.WAITMOTIONDONE_PERIOD)
        return False
