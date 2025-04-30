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

import os
import numpy as np


from pyicub.core.logger import YarpLogger

LOGGER = YarpLogger.getLogger()

#LOGGER.setLevel(logging.INFO)

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

    def isValid(self):
        return self.__rpcPort__.connection_result

    def say(self, something, waitActionDone=True):
        self.__port__.write("\"%s\"" % something)
        btl = yarp.Bottle()
        btl.clear()
        btl.addString("stat")
        res = self.__rpcPort__.execute(btl)
        if waitActionDone:
            if res.toString() == "quiet":
                while res.toString() != "speaking":
                    res = self.__rpcPort__.execute(btl)
                    yarp.delay(0.01)
            while res.toString() == "speaking":
                res = self.__rpcPort__.execute(btl)
                yarp.delay(0.01)
        return res.toString()

    def say_from_file(self, abs_file_path, wait_action_done=True):
        text = None

        file_or_folder_exist = os.path.exists(abs_file_path)
        if not file_or_folder_exist:
            LOGGER.error(f"{abs_file_path} does not exist. Make sure to use an absolute path.")
            return "ERROR"

        is_file = os.path.isfile(abs_file_path)
        if not is_file:
            LOGGER.error(f"{abs_file_path} is not a file but a folder. Use `say_from_folder_rnd()` instead")
            return "ERROR"

        with open(abs_file_path, 'r') as f:
            text = f.read()
            text = text.strip() # remove characters such as '\n'
        
        if len(text) == 0:
            LOGGER.warning(f"{abs_file_path} is an empty file!")

        LOGGER.info(f"Speaking from {abs_file_path} file")
        return self.say(something=text, waitActionDone=wait_action_done)
    
    def say_from_folder_rnd(self, abs_folder_path, random_seed=0, wait_action_done=True):
        random_gen = np.random.default_rng(seed=random_seed)

        file_or_folder_exist = os.path.exists(abs_folder_path)
        if not file_or_folder_exist:
            LOGGER.error(f"{abs_folder_path} does not exist. Make sure to use an absolute path.")
            return "ERROR"

        is_file = os.path.isfile(abs_folder_path)
        if is_file:
            LOGGER.error(f"{abs_folder_path} is not a file but a folder. Use `say_from_file()` instead")
            return "ERROR"

        filename = random_gen.choice(os.listdir(abs_folder_path))
        filepath = os.path.join(abs_folder_path, filename)

        return self.say_from_file(filepath, wait_action_done=wait_action_done)

    def close(self):
        self.__port__.close()
