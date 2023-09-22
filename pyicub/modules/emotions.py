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

import yarp
from pyicub.core.rpc import RpcClient


class emotionsPyCtrl:

    def __init__(self, robot):
        self.__rpc__ = RpcClient("/%s/face/emotions/in" % robot)

    def isValid(self):
        return self.__rpc__.connection_result
        
    def __emoCmd__(self, part, emo):
        cmd = yarp.Bottle()
        cmd.clear()
        cmd.addString("set")
        cmd.addString(part)
        cmd.addString(emo)
        return self.__rpc__.execute(cmd)

    def smile(self):
        self.__emoCmd__("all", "hap")

    def eb_smile(self):
        self.__emoCmd__("leb", "hap")
        self.__emoCmd__("reb", "hap")

    def eb_surprised(self):
        self.__emoCmd__("leb", "sur")
        self.__emoCmd__("reb", "sur")

    def surprised(self):
        self.__emoCmd__("mou", "sur")
        self.__emoCmd__("leb", "sur")
        self.__emoCmd__("reb", "sur")

    def neutral(self):
        self.__emoCmd__("mou", "neu")
        self.__emoCmd__("leb", "neu")
        self.__emoCmd__("reb", "neu")

    def sad(self):
        self.__emoCmd__("mou", "sad")
        self.__emoCmd__("leb", "sad")
        self.__emoCmd__("reb", "sad")

    def openingEyes(self):
        self.__emoCmd__("eli", "hap")

    def closingEyes(self):
        self.__emoCmd__("eli", "sad")

    def cun(self):
        self.__emoCmd__("leb", "cun")
        self.__emoCmd__("reb", "cun")

    def angry(self):
        self.__emoCmd__("all", "ang")

    def evil(self):
        self.__emoCmd__("all", "evil")

    def sendCmd(self, part, emo):
        return self.__emoCmd__(part, emo)

    #set col <color>     set the color of the led
    #        !! available only for rfe board !!
    #        the available colors are: black, white, red, lime, blue, yellow, cyan, magenta, silver, gray, maroon, olive, green, purple, teal, navy
    def setColor(self, color):
        return self.__emoCmd__("col", color)

    #set brig <brig>       set the brightness of the leds
    #    !! available only for rfe board !!
    #    the brightness is defined by an integer from 0 to 5, where 0 means led off
    def setBrightness(self, brightness):
        return self.__emoCmd__("brig", brightness)
