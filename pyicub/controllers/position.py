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


class JointPoseVel:

    def __init__(self, target_position, vel_list, joints_list=None):
        self.target_position = target_position
        self.vel_list = vel_list
        self.joints_list = joints_list

class JointsTrajectoryCheckpoint:

    def __init__(self, pose: JointPose, duration: float, timeout: float=0.0):
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
        self.__driver__     = self._getDriver_()
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

    def move(self, pose: JointPose, req_time: float, timeout: float=0.0, waitMotionDone: bool=True):
        self.__mot_id__ += 1
        target_joints = pose.target_joints
        joints_list = pose.joints_list
        if timeout == 0.0:
            timeout = PositionController.DEFAULT_TIMEOUT
        self.__logger__.info("""Motion <%d> STARTED!
                              robot_part:%s, 
                              target_joints:%s
                              req_time:%.2f,
                              joints_list=%s,
                              waitMotionDone=%s""" %
                              (self.__mot_id__,
                              self.__robot_part__.name,
                              str(target_joints),
                              req_time,
                              str(joints_list),
                              str(waitMotionDone)) )
        if joints_list is None:
            joints_list = range(0, self.__joints__)
        disp  = [0]*len(joints_list)
        speed = [0]*len(joints_list)
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
            speed[i] = disp[i]/req_time
            self.__IPositionControl__.setRefSpeed(j, speed[i])
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
                                    waitMotionDone=%s""" %
                                    (self.__mot_id__,
                                    self.__robot_part__.name,
                                    str(target_joints),
                                    req_time,
                                    str(joints_list),
                                    str(waitMotionDone)) )
            else:
                self.__logger__.warning("""Motion <%d> TIMEOUT!
                                    robot_part:%s, 
                                    target_joints:%s
                                    joints_list=%s""" %
                                    (self.__mot_id__,
                                    self.__robot_part__.name,
                                    str(target_joints),
                                    str(joints_list)) )



    
    def moveRefVel(self, pose: JointPoseVel, req_time: float, timeout: float=0.0, waitMotionDone: bool=True):
        target_joints = pose.target_joints
        vel_list = pose.vel_list
        joints_list = pose.joints_list
        if timeout == 0.0:
            timeout = PositionController.DEFAULT_TIMEOUT
        self.__logger__.info("""Motion <%d> STARTED!
                              robot_part:%s, 
                              target_joints:%s
                              req_time:%.2f,
                              vel_list=%s,
                              waitMotionDone=%s""" %
                              (self.__mot_id__,
                              self.__robot_part__.name,
                              str(target_joints),
                              req_time,
                              str(vel_list),
                              str(waitMotionDone)) )

        if joints_list is None:
            joints_list = range(0, self.__joints__)
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
            self.waitMotionDone(target_joints, joints_list, timeout=timeout)
        self.__logger__.info("""Motion <%d> COMPLETED!
                              robot_part:%s, 
                              target_joints:%s
                              req_time:%.2f,
                              vel_list=%s,
                              waitMotionDone=%s""" %
                              (self.__mot_id__,
                              self.__robot_part__.name,
                              str(target_joints),
                              req_time,
                              str(vel_list),
                              str(waitMotionDone)) )
    

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
