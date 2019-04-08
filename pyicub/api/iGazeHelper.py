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

class iGazeHelper:

    def __init__(self, gaze_controller):
        self.__gaze_controller__ = gaze_controller.getIGazeControl()

    def blockEyes(self, vergence):
        self.__gaze_controller__.blockEyes(vergence)

    def blockNeck(self):
        self.__gaze_controller__.blockNeckYaw()
        self.__gaze_controller__.blockNeckRoll()
        self.__gaze_controller__.blockNeckPitch()

    def clearEyes(self):
        self.__gaze_controller__.clearEyes()

    def clearNeck(self):
        self.__gaze_controller__.clearNeckYaw()
        self.__gaze_controller__.clearNeckRoll()
        self.__gaze_controller__.clearNeckPitch()

    def lookAt3DPoint(self, x, y, z):
        p = yarp.Vector(3)
        p.set(0, x)
        p.set(1, y)
        p.set(2, z)
        self.__gaze_controller__.lookAtFixationPoint(p)

    def lookAt3DPointSync(self, x, y, z, timeout=0.0):
        self.lookAt3DPoint(x, y, z)
        self.__gaze_controller__.waitMotionDone(timeout)

    def reset(self):
        self.clearEyes()
        self.clearNeck()

    def setParams(self, neck_tt, eyes_tt):
        self.__gaze_controller__.setNeckTrajTime(neck_tt)
        self.__gaze_controller__.setEyesTrajTime(eyes_tt)

    def setTrackingMode(self, mode):
        self.__gaze_controller__.setTrackingMode(mode)
