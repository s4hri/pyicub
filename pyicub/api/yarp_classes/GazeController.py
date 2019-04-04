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

class GazeController:

    def __init__(self):
        self.__props__ = yarp.Property()
        self.__driver__ = yarp.PolyDriver()
        self.__props__.put("robot", "icub")
        self.__props__.put("device","gazecontrollerclient")
        self.__props__.put("local","/gaze_client")
        self.__props__.put("remote","/iKinGazeCtrl")

        self.__driver__.open(self.__props__)
        if not self.__driver__.isValid():
            print 'Cannot open GazeController driver!'
            sys.exit()
        self.__IGazeControl__ = self.__driver__.viewIGazeControl()

    def getIGazeControl(self):
        return self.__IGazeControl__

    def __del__(self):
        self.__driver__.close()
