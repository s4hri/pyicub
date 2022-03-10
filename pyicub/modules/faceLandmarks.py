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

from pyicub.core.ports import BufferedReadPort

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
