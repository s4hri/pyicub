# BSD 2-Clause License
#
# Copyright (c) 2024, Social Cognition in Human-Robot Interaction,
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

try:
    import yarp
except ImportError:
    pass

import os
import time
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
    def __init__(self, name, robot_part, joints_nr, joints_list, joints_speed):
        self.name = name
        self.robot_part = robot_part
        self.joints_nr = joints_nr
        self.joints_list = joints_list
        self.joints_speed = joints_speed

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

ICUB_EYELIDS        = iCubPart('EYELIDS',       ICUB_PARTS.FACE       ,  1,  [0], [10])
ICUB_HEAD           = iCubPart('HEAD',          ICUB_PARTS.HEAD       ,  6,  [0, 1, 2, 3, 4, 5], [10, 10, 20, 20, 20, 20])
ICUB_EYES           = iCubPart('EYES',          ICUB_PARTS.HEAD       ,  3,  [3, 4, 5], [20, 20, 20])
ICUB_NECK           = iCubPart('NECK',          ICUB_PARTS.HEAD       ,  3,  [0, 1, 2], [10, 10, 20])
ICUB_LEFTARM_FULL   = iCubPart('LEFTARM_FULL',  ICUB_PARTS.LEFT_ARM   ,  16, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], [25, 25, 25, 25, 40, 40, 40, 100, 100, 100, 100, 100, 100, 100, 100, 100])
ICUB_LEFTHAND       = iCubPart('LEFTHAND',      ICUB_PARTS.LEFT_ARM   ,  8,  [8, 9, 10, 11, 12, 13, 14, 15], [100, 100, 100, 100, 100, 100, 100, 100])
ICUB_LEFTARM        = iCubPart('LEFTARM',       ICUB_PARTS.LEFT_ARM   ,  8,  [0, 1, 2, 3, 4, 5, 6, 7], [25, 25, 25, 25, 40, 40, 40, 100])
ICUB_RIGHTARM_FULL  = iCubPart('RIGHTARM_FULL', ICUB_PARTS.RIGHT_ARM  ,  16, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], [25, 25, 25, 25, 40, 40, 40, 100, 100, 100, 100, 100, 100, 100, 100, 100])
ICUB_RIGHTHAND      = iCubPart('RIGHTHAND',     ICUB_PARTS.RIGHT_ARM  ,  8,  [8, 9, 10, 11, 12, 13, 14, 15], [100, 100, 100, 100, 100, 100, 100, 100])
ICUB_RIGHTARM       = iCubPart('RIGHTARM',      ICUB_PARTS.RIGHT_ARM  ,  8,  [0, 1, 2, 3, 4, 5, 6, 7], [25, 25, 25, 25, 40, 40, 40, 100])
ICUB_TORSO          = iCubPart('TORSO',         ICUB_PARTS.TORSO      ,  3,  [0, 1, 2], [10, 10, 10])
ICUB_LEFTLEG        = iCubPart('LEFTLEG',       ICUB_PARTS.LEFT_LEG   ,  6,  [0, 1, 2, 3, 4, 5], [10, 10, 10, 10, 10, 10])
ICUB_RIGHTLEG       = iCubPart('RIGHTLEG',      ICUB_PARTS.RIGHT_LEG  ,  6,  [0, 1, 2, 3, 4, 5], [10, 10, 10, 10, 10, 10])


class JointPose:

    def __init__(self, target_joints, joints_list=None):
        self.target_joints = target_joints
        self.joints_list = joints_list

    def toJSON(self):
        return self.__dict__



class RemoteControlboard:

    def __init__(self, robot_name, part):
        self.__robot_name__ = robot_name
        self.__part__ = part
        self.__pid__ = str(os.getpid())
        self.__driver__ = None
        props  = self._getRobotPartProperties_()
        self.__driver__ = yarp.PolyDriver(props)

    def __del__(self):
        self.__driver__.close()

    def _getRobotPartProperties_(self):
        props = yarp.Property()
        props.put("device","remote_controlboard")
        props.put("local","/pyicub/" + self.__pid__ + "/" + self.__robot_name__ + "/" + self.__part__.name)
        props.put("remote", "/" + self.__robot_name__ + "/" + self.__part__.robot_part)
        return props

    def getDriver(self):
        return self.__driver__

class PositionController:

    WAITMOTIONDONE_PERIOD = 0.01
    MOTION_COMPLETE_AT = 0.90

    def __init__(self, robot_name, part, logger):
        self.__part__ = part
        self.__logger__     = logger
        self.__driver__ = RemoteControlboard(robot_name, part)
        self.__IEncoders__        = None
        self.__IControlLimits__   = None
        self.__IControlMode__   = None
        self.__IPositionControl__   = None
        self.__joints__   = None
        self.__waitMotionDone__ = self.waitMotionDone

    def isValid(self):
        return self.PolyDriver.isValid()

    def init(self):
        self.__IEncoders__        = self.PolyDriver.viewIEncoders()
        self.__IControlLimits__   = self.PolyDriver.viewIControlLimits()
        self.__IControlMode__     = self.PolyDriver.viewIControlMode()
        self.__IPositionControl__ = self.PolyDriver.viewIPositionControl()
        self.__joints__           = self.__IPositionControl__.getAxes()
    
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
        return not self.__IPositionControl__.checkMotionDone()

    def __move__(self, target_joints, joints_list, req_time, joints_speed):

        disp  = [0]*len(joints_list)
        speeds = [0]*len(joints_list)
        times = [0]*len(joints_list)
        tmp   = yarp.Vector(self.__joints__)
        encs  = yarp.Vector(self.__joints__)

        while not self.__IEncoders__.getEncoders(encs.data()):
            yarp.delay(0.1)
        i = 0

        if req_time > 0.0:
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
            for j in joints_list:
                tmp.set(i, target_joints[i])
                disp[i] = float(target_joints[i] - encs[j])
                if disp[i] < 0.0:
                    disp[i] =- disp[i]
                if abs(disp[i]) > 0.001:
                    speeds[i] = joints_speed[i]
                    times[i] = disp[i]/speeds[i]
                    self.__IPositionControl__.setRefSpeed(j, speeds[i])
                    self.__IPositionControl__.positionMove(j, tmp[i])
                i+=1
            req_time = max(times)
        
        return req_time

    def stop(self, joints_list=None):
        t0 = time.perf_counter()
        if joints_list is None:
            joints_list = range(0, self.__joints__)
        for j in joints_list:
            self.__IPositionControl__.setRefSpeed(j, 0.0)
        return 0.0


    def move(self, pose: JointPose, req_time: float=0.0, timeout: float=DEFAULT_TIMEOUT, joints_speed: list=[], waitMotionDone: bool=True, tag: str='default'):
        t0 = time.perf_counter()
        target_joints = pose.target_joints
        joints_list = pose.joints_list
        if joints_list is None:
            joints_list = range(0, self.__joints__)

        self.setPositionControlMode(joints_list=joints_list)
            
        if not joints_speed:
            for j in joints_list:
                ref_speed = 10.0
                joints_speed.append(ref_speed)

        self.__logger__.info("""Motion STARTED!
                                tag: %s,
                                robot_part:%s,
                                target_joints:%s,
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s,
                                speed=%s""" %
                                (
                                  tag,
                                  self.__part__.name,
                                  str(target_joints)      ,
                                  req_time                ,
                                  str(joints_list)        ,
                                  str(waitMotionDone)     ,
                                  str(timeout)            ,
                                  str(joints_speed)
                                )
                            )

        req_time = self.__move__(target_joints, joints_list, req_time, joints_speed)

        if waitMotionDone is True:
            res = self.__waitMotionDone__(req_time=req_time, timeout=timeout)
            elapsed_time = time.perf_counter() - t0
            if res:
                self.__logger__.info("""Motion COMPLETED!
                                elapsed_time: %s,
                                tag: %s,
                                robot_part:%s,
                                target_joints:%s
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s,
                                speed=%s""" %
                                (
                                    elapsed_time,
                                    tag,
                                    self.__part__.name,
                                    str(target_joints)      ,
                                    req_time                ,
                                    str(joints_list)        ,
                                    str(waitMotionDone)     ,
                                    str(timeout),
                                    str(joints_speed)
                                ))
            else:
                self.__logger__.warning("""Motion TIMEOUT!
                                elapsed_time: %s,
                                tag: %s,
                                robot_part:%s,
                                target_joints:%s
                                req_time:%.2f,
                                joints_list=%s,
                                waitMotionDone=%s,
                                timeout=%s,
                                speed=%s""" %
                                (
                                    elapsed_time,
                                    tag,
                                    self.__part__.name,
                                    str(target_joints)      ,
                                    req_time                ,
                                    str(joints_list)        ,
                                    str(waitMotionDone)     ,
                                    str(timeout),
                                    str(joints_speed)
                                ))
            return res
                

    def setPositionControlMode(self, joints_list):
        for j in joints_list:
            self.__IControlMode__.setControlMode(j, yarp.VOCAB_CM_POSITION)

    def setCustomWaitMotionDone(self, motion_complete_at=MOTION_COMPLETE_AT):
        self.__waitMotionDone__ = self.waitMotionDone2
        PositionController.MOTION_COMPLETE_AT = motion_complete_at

    def unsetCustomWaitMotionDone(self):
        self.__waitMotionDone__ = self.waitMotionDone

    def waitMotionDone(self, req_time: float=DEFAULT_TIMEOUT, timeout: float=DEFAULT_TIMEOUT):
        t0 = time.perf_counter()
        elapsed_time = 0.0
        while elapsed_time < timeout:
            if not self.isMoving():
                return True
            yarp.delay(PositionController.WAITMOTIONDONE_PERIOD)
            elapsed_time = time.perf_counter() - t0
        
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
