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


DEFAULT_TIMEOUT = 30.0

class ICUB_PARTS:
    HEAD       = 'head'
    FACE       = 'face'
    TORSO      = 'torso'
    LEFT_ARM   = 'left_arm'
    RIGHT_ARM  = 'right_arm'
    LEFT_LEG   = 'left_leg'
    RIGHT_LEG  = 'right_leg'

class iCubPart:
    def __init__(self, name, robot_part, joints_nr, joints_list):
        self.name = name
        self.robot_part = robot_part
        self.joints_nr = joints_nr
        self.joints_list = joints_list

    def toJSON(self):
        return self.__dict__

ICUB_EYELIDS        = iCubPart('EYELIDS',       ICUB_PARTS.FACE       ,  1,  [0] )
ICUB_HEAD           = iCubPart('HEAD',          ICUB_PARTS.HEAD       ,  6,  [0, 1, 2, 3, 4, 5])
ICUB_EYES           = iCubPart('EYES',          ICUB_PARTS.HEAD       ,  3,  [3, 4, 5])
ICUB_NECK           = iCubPart('NECK',          ICUB_PARTS.HEAD       ,  3,  [0, 1, 2])
ICUB_LEFTARM_FULL   = iCubPart('LEFTARM_FULL',  ICUB_PARTS.LEFT_ARM   , 16,  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
ICUB_LEFTHAND       = iCubPart('LEFTHAND',      ICUB_PARTS.LEFT_ARM   , 16,  [8, 9, 10, 11, 12, 13, 14, 15])
ICUB_LEFTARM        = iCubPart('LEFTARM',       ICUB_PARTS.LEFT_ARM   , 16,  [0, 1, 2, 3, 4, 5, 6, 7])
ICUB_RIGHTARM_FULL  = iCubPart('RIGHTARM_FULL', ICUB_PARTS.RIGHT_ARM  , 16,  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
ICUB_RIGHTHAND      = iCubPart('RIGHTHAND',     ICUB_PARTS.RIGHT_ARM  , 16,  [8, 9, 10, 11, 12, 13, 14, 15])
ICUB_RIGHTARM       = iCubPart('RIGHTARM',      ICUB_PARTS.RIGHT_ARM  , 16,  [0, 1, 2, 3, 4, 5, 6, 7])
ICUB_TORSO          = iCubPart('TORSO',         ICUB_PARTS.TORSO      ,  3,  [0, 1, 2])
ICUB_LEFTLEG        = iCubPart('LEFTLEG',       ICUB_PARTS.LEFT_LEG   ,  6,  [0, 1, 2, 3, 4, 5])
ICUB_RIGHTLEG       = iCubPart('RIGHTLEG',      ICUB_PARTS.RIGHT_LEG  ,  6,  [0, 1, 2, 3, 4, 5])


class JointPose:

    def __init__(self, target_joints, joints_list=None):
        self.target_joints = target_joints
        self.joints_list = joints_list

    def toJSON(self):
        return self.__dict__



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
        props.put("local","/pyicub/" + self.__pid__ + self.__port_name__)
        props.put("remote", self.__port_name__)
        return props

    def getDriver(self):
        return self.__driver__

class PositionController:

    WAITMOTIONDONE_PERIOD = 0.1
    MOTION_COMPLETE_AT = 0.9

    def __init__(self, robot_name, part, logger):
        self.__part_name__ = part
        self.__logger__     = logger
        port_name = "/" + robot_name + "/" + part
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
        self.__control_modes__    = yarp.IVector(self.__joints__, yarp.VOCAB_CM_POSITION)

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

    def __move__(self, target_joints, joints_list, req_time, speed):
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
            disp[i] = float(target_joints[i] - encs[j])
            if disp[i] < 0.0:
                disp[i] =- disp[i]
            if abs(disp[i]) > 0.001:
                if req_time > 0.0:
                    speeds[i] = disp[i]/req_time
                else:
                    speeds[i] = speed
                    times[i] = disp[i]/speeds[i]
                self.__IPositionControl__.setRefSpeed(j, speeds[i])
                self.__IPositionControl__.positionMove(j, tmp[i])
            i+=1
        if req_time == 0:
            req_time = max(times)
        return req_time

    def stop(self, joints_list=None):
        t0 = time.perf_counter()
        if joints_list is None:
            joints_list = range(0, self.__joints__)
        for j in joints_list:
            self.__IPositionControl__.setRefSpeed(j, 0.0)
        return 0.0


    def move(self, pose: JointPose, req_time: float=0.0, timeout: float=DEFAULT_TIMEOUT, speed: float=10.0, waitMotionDone: bool=True, tag: str='default'):
        t0 = time.perf_counter()
        self.setPositionControlMode()
        target_joints = pose.target_joints
        joints_list = pose.joints_list
        if joints_list is None:
            joints_list = range(0, self.__joints__)
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

        req_time = self.__move__(target_joints, joints_list, req_time, speed)

        if waitMotionDone is True:
            res = self.__waitMotionDone__(req_time=req_time, timeout=timeout)
            if res:
                self.__logger__.info("""Motion COMPLETED!
                                elapsed_time: %s,
                                tag: %s,
                                robot_part:%s,
                                target_joints:%s
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s""" %
                                (
                                    time.perf_counter() - t0,
                                    tag,
                                    self.__part_name__,
                                    str(target_joints)      ,
                                    req_time                ,
                                    str(joints_list)        ,
                                    str(waitMotionDone)     ,
                                    str(timeout)
                                ))
            else:
                self.stop()
                self.__logger__.warning("""Motion TIMEOUT!
                                elapsed_time: %s,
                                tag: %s,
                                robot_part:%s,
                                target_joints:%s
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s""" %
                                (
                                    time.perf_counter() - t0,
                                    tag,
                                    self.__part_name__,
                                    str(target_joints)      ,
                                    req_time                ,
                                    str(joints_list)        ,
                                    str(waitMotionDone)     ,
                                    str(timeout)
                                ))
            return res
                

    def setPositionControlMode(self):
        self.__IControlMode__.setControlModes(self.__control_modes__)

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
