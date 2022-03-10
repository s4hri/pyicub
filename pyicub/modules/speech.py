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

from multiprocessing.connection import wait
import yarp
from pyicub.core.ports import BufferedWritePort
from pyicub.core.rpc import RpcClient

class speechPyCtrl:

    def __init__(self, robot):
         self.__port__ = BufferedWritePort("/pyicub/speech:o", "/%s/speech:rpc" % robot)

    def say(self, something):
        self.__port__.write("say \"%s\"" % something)

    def setPitch(self, pitch):
        self.__port__.write("setPitch %d" % pitch)

    def setSpeed(self, speed):
        self.__port__.write("setSpeed %d" % speed)

    def close(self):
        self.__port__.close()

class iSpeakPyCtrl:

    def __init__(self):
         self.__port__ = BufferedWritePort("/pyicub/speech:o", "/iSpeak")
         self.__rpcPort__ = RpcClient("/iSpeak/rpc")

    def say(self, something, waitActionDone=True):
        self.__port__.write("\"%s\"" % something)
        btl = yarp.Bottle()
        btl.clear()
        btl.addString("stat")
        res = self.__rpcPort__.execute(btl)
        if waitActionDone:
            while res.toString() == "speaking":
                res = self.__rpcPort__.execute(btl)
                yarp.delay(0.01)
        return res

    def close(self):
        self.__port__.close()
