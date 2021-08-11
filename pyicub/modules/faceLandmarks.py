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

from pyicub.core.BufferedPort import BufferedReadPort

class faceLandmarksPyCtrl:

    def __init__(self):
        self.__landmarks__ = []
        self.__faces__     = 0
        self.__port_landmarks__ = BufferedReadPort("/faceLandmarksPyCtrl/landmarks:i", "/faceLandmarks/landmarks:o", callback=self.onRead)
        self.__port_faces__     = BufferedReadPort("/faceLandmarksPyCtrl/faces:i", "/faceLandmarks/faces:o", callback=self.onReadFaces)

## LANDMARKS
    def onRead(self, bottle):
        self.__landmarks__ = []
        for i in range(bottle.size()):
            self.__landmarks__.append(bottle.get(i).asList())

    def getLandmark(self, landmark_index, face_index = 0):
        if self.__landmarks__:
            x = self.__landmarks__[face_index].get(landmark_index).asList().get(0).asInt32()
            y = self.__landmarks__[face_index].get(landmark_index).asList().get(1).asInt32()
            return [x, y]
        else:
            return [None, None]
    
    def getCenterEyes(self, face_index = 0):
        [x, y] = self.getLandmark(27, face_index)
        return [x, y]

## FACES
    def onReadFaces(self, bottle):
        self.__faces__= bottle.get(0).asInt32()
    
    def getFaces(self):
        return self.__faces__