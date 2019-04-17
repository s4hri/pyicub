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
import sys
import time

from Generics import GenericController

class GazeController(GenericController):

    TIMEOUT_PERIOD = 0.1

    def __init__(self, robot, logger):
        GenericController.__init__(self, logger)
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

    def __waitMotionDone__(self, timeout):
        res = self.__IGazeControl__.waitMotionDone(GazeController.TIMEOUT_PERIOD, timeout)
        if res is False:
            self.__logger__.error("Timeout occurred!")

    @GenericController.__atomicDecorator__
    def blockEyes(self, vergence):
        self.__IGazeControl__.blockEyes(vergence)

    @GenericController.__atomicDecorator__
    def blockNeck(self):
        self.__IGazeControl__.blockNeckYaw()
        self.__IGazeControl__.blockNeckRoll()
        self.__IGazeControl__.blockNeckPitch()

    @GenericController.__atomicDecorator__
    def clearEyes(self):
        self.__IGazeControl__.clearEyes()

    @GenericController.__atomicDecorator__
    def clearNeck(self):
        self.__IGazeControl__.clearNeckYaw()
        self.__IGazeControl__.clearNeckRoll()
        self.__IGazeControl__.clearNeckPitch()

    def getIGazeControl(self):
        return self.__IGazeControl__

    @GenericController.__atomicDecorator__
    def lookAt3DPoint(self, x, y, z, waitMotionDone=False, timeout=0.0):
        p = yarp.Vector(3)
        p.set(0, x)
        p.set(1, y)
        p.set(2, z)
        self.__IGazeControl__.lookAtFixationPoint(p)
        if waitMotionDone is True:
            self.__waitMotionDone__(timeout)

    def reset(self):
        self.clearEyes()
        self.clearNeck()

    @GenericController.__atomicDecorator__
    def setParams(self, neck_tt, eyes_tt):
        self.__IGazeControl__.setNeckTrajTime(neck_tt)
        self.__IGazeControl__.setEyesTrajTime(eyes_tt)

    @GenericController.__atomicDecorator__
    def setTrackingMode(self, mode):
        self.__IGazeControl__.setTrackingMode(mode)

    def __del__(self):
        self.__driver__.close()
