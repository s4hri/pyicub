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

class GazeMotion:
    def __init__(self, lookat_method: str):
        self.checkpoints = []
        self.lookat_method = lookat_method

    def addCheckpoint(self, value: list):
        self.checkpoints.append(value)


class GazeController:

    WAITMOTION_PERIOD = 0.01
    WAITMOTIONDONE_TIMEOUT = 2.0

    def __init__(self, robot, logger=YarpLogger.getLogger()):
        self.__logger__ = logger
        self.__props__ = yarp.Property()
        self.__driver__ = yarp.PolyDriver()
        self.__props__.put("robot", robot)
        self.__props__.put("device","gazecontrollerclient")
        self.__props__.put("local","/gaze_client")
        self.__props__.put("remote","/iKinGazeCtrl")
        self.__driver__.open(self.__props__)
        if not self.__driver__.isValid():
            self.__logger__.error('Cannot open GazeController driver!')
        else:
            self.__IGazeControl__ = self.__driver__.viewIGazeControl()
            self.__IGazeControl__.setTrackingMode(False)
            self.__IGazeControl__.stopControl()
            self.clearNeck()
            self.clearEyes()

    @property
    def IGazeControl(self):
        return self.__IGazeControl__

    def __lookAtAbsAngles__(self, angles, waitMotionDone=True):
        self.__logger__.info("""Looking at angles STARTED!
                                 angles=%s, waitMotionDone=%s""" % (str([angles[0], angles[1], angles[2]]), str(waitMotionDone)) )
        self.IGazeControl.lookAtAbsAngles(angles)
        if waitMotionDone is True:
            self.waitMotionDone(angles)
        self.__logger__.info("""Looking at angles COMPLETED!
                                 angles=%s, waitMotionDone=%s""" % (str([angles[0], angles[1], angles[2]]), str(waitMotionDone)) )

    def __lookAtRelAngles__(self, angles, waitMotionDone=True):
        self.__logger__.info("""Looking at angles STARTED!
                                 angles=%s, waitMotionDone=%s""" % (str([angles[0], angles[1], angles[2]]), str(waitMotionDone)) )
        self.IGazeControl.lookAtRelAngles(angles)
        if waitMotionDone is True:
            self.waitMotionDone(angles)
        self.__logger__.info("""Looking at angles COMPLETED!
                                 angles=%s, waitMotionDone=%s""" % (str([angles[0], angles[1], angles[2]]), str(waitMotionDone)) )

    def blockEyes(self, vergence):
        self.IGazeControl.blockEyes(vergence)

    def blockNeck(self):
        self.IGazeControl.blockNeckYaw()
        self.IGazeControl.blockNeckRoll()
        self.IGazeControl.blockNeckPitch()

    def clearEyes(self):
        self.IGazeControl.clearEyes()

    def clearNeck(self):
        self.IGazeControl.clearNeckYaw()
        self.IGazeControl.clearNeckRoll()
        self.IGazeControl.clearNeckPitch()

    def lookAtAbsAngles(self, azi, ele, ver, waitMotionDone=True):
        angles = yarp.Vector(3)
        angles.set(0, azi)
        angles.set(1, ele)
        angles.set(2, ver)
        self.__lookAtAbsAngles__(angles, waitMotionDone)

    def lookAtRelAngles(self, azi, ele, ver, waitMotionDone=True):
        angles = yarp.Vector(3)
        angles.set(0, azi)
        angles.set(1, ele)
        angles.set(2, ver)
        self.__lookAtRelAngles__(angles, waitMotionDone)

    def lookAtFixationPoint(self, x, y, z, waitMotionDone=True):
        p = yarp.Vector(3)
        p.set(0, x)
        p.set(1, y)
        p.set(2, z)
        angles = yarp.Vector(3)
        self.IGazeControl.getAnglesFrom3DPoint(p, angles)
        self.__lookAtAbsAngles__(angles, waitMotionDone)

    def reset(self):
        self.clearEyes()
        self.clearNeck()

    def setParams(self, neck_tt, eyes_tt):
        self.IGazeControl.setNeckTrajTime(neck_tt)
        self.IGazeControl.setEyesTrajTime(eyes_tt)

    def setTrackingMode(self, mode):
        self.IGazeControl.setTrackingMode(mode)

    def waitMotionDone(self, target_angles, period=WAITMOTION_PERIOD, timeout=WAITMOTIONDONE_TIMEOUT):
        self.__logger__.info("""Waiting for motion done STARTED! target_angles: %s""" % str([target_angles[0], target_angles[1], target_angles[2]]))
        res = self.IGazeControl.waitMotionDone(period=period, timeout=timeout)
        self.__logger__.info("""Motion done DETECTED! target_angles: %s""" % str([target_angles[0], target_angles[1], target_angles[2]]))
        return res

    def waitMotionOnset(self, speed_ref=0, period=WAITMOTION_PERIOD, max_attempts=50):
        self.__logger__.info("""Waiting for gaze motion onset STARTED!
                                 speed_ref=%s""" % str(speed_ref))
        q = yarp.Vector(6)
        for _ in range(0, max_attempts):
            self.IGazeControl.getJointsVelocities(q)
            v = []
            for i in range(0,6):
                v.append(q[i])
            speed = utils.norm(v)
            if speed > speed_ref:
                self.__logger__.info("""Motion onset DETECTED! speed_ref=%s""" % str(speed_ref))
                return True
            yarp.delay(period)
        self.__logger__.warning("""Motion onset TIMEOUT! speed_ref=%s""" % str(speed_ref))
        return False
