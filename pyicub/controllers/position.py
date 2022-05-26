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
import concurrent.futures

import pyicub.utils as utils


DEFAULT_TIMEOUT = 30.0

class JointPose:

    def __init__(self, target_joints, joints_list=None):
        self.target_joints = target_joints
        self.joints_list = joints_list


class RemoteControlboard:

    def __init__(self, port_name):
        self.__pid__ = str(os.getpid())
        self.__port_name__ = port_name
        self.__driver__ = None
        props  = self._getRobotPartProperties_()
        self.__driver__ = yarp.PolyDriver(props)

    def __del__(self):
        self.__driver__.close()

    def _getRobotPartProperties_(self):
        props = yarp.Property()
        props.put("device","remote_controlboard")
        props.put("local","/client/" + self.__pid__ + self.__port_name__)
        props.put("remote", self.__port_name__)
        return props

    def getDriver(self):
        return self.__driver__

class PositionController:

    WAITMOTIONDONE_PERIOD = 0.1
    MOTION_COMPLETE_AT = 0.9

    def __init__(self, robot_name, part_name, logger):
        self.__part_name__ = part_name
        self.__logger__     = logger
        port_name = "/" + robot_name + "/" + part_name
        self.__driver__ = RemoteControlboard(port_name)
        self.__IEncoders__        = None
        self.__IControlLimits__   = None
        self.__IControlMode__   = None
        self.__IPositionControl__   = None
        self.__joints__   = None
        self.__waitMotionDone__ = self.waitMotionDone2

    def isValid(self):
        return self.PolyDriver.isValid()

    def init(self):
        self.__IEncoders__        = self.PolyDriver.viewIEncoders()
        self.__IControlLimits__   = self.PolyDriver.viewIControlLimits()
        self.__IControlMode__     = self.PolyDriver.viewIControlMode()
        self.__IPositionControl__ = self.PolyDriver.viewIPositionControl()
        self.__joints__           = self.__IPositionControl__.getAxes()
        self.__setPositionControlMode__(self.__joints__)

    def __setPositionControlMode__(self, joints):
        modes = yarp.IVector(joints, yarp.VOCAB_CM_POSITION)
        self.__IControlMode__.setControlModes(modes)

    @property
    def PolyDriver(self):
        return self.__driver__.getDriver()

    def getIPositionControl(self):
        return self.__IPositionControl__

    def getIEncoders(self):
        return self.__IEncoders__

    def getIControlLimits(self):
        return self.__IControlLimits__

    def isMoving(self):
        return self.__IPositionControl__.checkMotionDone()

    def move(self, pose: JointPose, req_time: float=0.0, timeout: float=DEFAULT_TIMEOUT, speed: float=10.0, waitMotionDone: bool=True, tag: str='default'):
        target_joints = pose.target_joints
        joints_list = pose.joints_list
        self.__logger__.info("""Motion STARTED!
                                tag: %s,
                                robot_part:%s,
                                target_joints:%s,
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s""" %
                                (
                                  tag,
                                  self.__part_name__,
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
                yarp.delay(0.1)
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
            disp  = [0]*len(joints_list)
            speeds = [0]*len(joints_list)
            times = [0]*len(joints_list)
            tmp   = yarp.Vector(self.__joints__)
            encs  = yarp.Vector(self.__joints__)
            while not self.__IEncoders__.getEncoders(encs.data()):
                yarp.delay(0.1)
            i = 0
            for j in joints_list:
                tmp.set(i, target_joints[i])
                disp[i] = target_joints[i] - encs[j]
                if disp[i] < 0.0:
                    disp[i] =- disp[i]
                speeds[i] = speed
                times[i] = disp[i]/speeds[i]
                self.__IPositionControl__.setRefSpeed(j, speeds[i])
                self.__IPositionControl__.positionMove(j, tmp[i])
                i+=1
            req_time = max(times)

        if waitMotionDone is True:
            res = self.__waitMotionDone__(req_time=req_time, timeout=timeout)
            if res:
                self.__logger__.info("""Motion COMPLETED!
                                tag: %s,
                                robot_part:%s,
                                target_joints:%s
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s""" %
                                (
                                    tag,
                                    self.__part_name__,
                                    str(target_joints)      ,
                                    req_time                ,
                                    str(joints_list)        ,
                                    str(waitMotionDone)     ,
                                    str(timeout)
                                ))
            else:
                self.__logger__.warning("""Motion TIMEOUT!
                                tag: %s,
                                robot_part:%s,
                                target_joints:%s
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s""" %
                                (
                                    tag,
                                    self.__part_name__,
                                    str(target_joints)      ,
                                    req_time                ,
                                    str(joints_list)        ,
                                    str(waitMotionDone)     ,
                                    str(timeout)
                                ))
            return res
                


    def setCustomWaitMotionDone(self, motion_complete_at=MOTION_COMPLETE_AT):
        self.__waitMotionDone__ = self.waitMotionDone2
        PositionController.MOTION_COMPLETE_AT = motion_complete_at

    def unsetCustomWaitMotionDone(self):
        self.__waitMotionDone__ = self.waitMotionDone

    def waitMotionDone(self, req_time: float=DEFAULT_TIMEOUT, timeout: float=DEFAULT_TIMEOUT):
        t0 = time.perf_counter()
        while (time.perf_counter() - t0) < timeout:
            if self.__IPositionControl__.checkMotionDone():
                return True
            yarp.delay(PositionController.WAITMOTIONDONE_PERIOD)
        return False

    def waitMotionDone2(self, req_time: float=DEFAULT_TIMEOUT, timeout: float=DEFAULT_TIMEOUT):
        t0 = time.perf_counter()
        target_pos = yarp.Vector(self.__joints__)
        encs=yarp.Vector(self.__joints__)
        self.__IPositionControl__.getTargetPositions(target_pos.data())
        count = 0
        deadline = min(timeout, req_time)
        while (time.perf_counter() - t0) < deadline:
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
        if (time.perf_counter() - t0) > timeout:
            return False
        else:
            return True

    def waitMotionDone3(self, req_time: float=DEFAULT_TIMEOUT, timeout: float=DEFAULT_TIMEOUT):
        onset = False
        offset = False
        t0 = time.perf_counter()
        vel= yarp.Vector(self.__joints__)
        while (time.perf_counter() - t0) < timeout:
            self.__IEncoders__.getEncoderSpeeds(vel.data())
            v = []
            for i in range(0, self.__joints__):
                v.append(vel[i])
            if not onset:
                if utils.norm(v) > 0:
                    onset = True
            elif onset and (not offset):
                if utils.norm(v) == 0:
                    offset = True
                    break
            yarp.delay(PositionController.WAITMOTIONDONE_PERIOD)
        return onset and offset

    def waitMotionDone4(self, req_time: float=DEFAULT_TIMEOUT, timeout: float=DEFAULT_TIMEOUT):
        yarp.delay(req_time)
        return True
