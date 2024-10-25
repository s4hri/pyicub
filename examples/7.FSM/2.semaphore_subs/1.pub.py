# BSD 2-Clause License
#
# Copyright (c) 2024, Social Cognition in Human-Robot Interaction,
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

from pyicub.rest import PyiCubRESTfulServer
from pyicub.fsm import FSM
from datetime import date

import time
import logging

logger = logging.getLogger("FSM/SEMAPHORE")

class Semaphore(FSM):

    def __init__(self):
        FSM.__init__(self, name="Semaphore")
        self.addState(name="RED", on_enter_callback=self.on_RED)
        self.addState(name="YELLOW", on_enter_callback=self.on_YELLOW)
        self.addState(name="GREEN", on_enter_callback=self.on_GREEN)

        self.addTransition("start", "init", "RED")
        self.addTransition("go", "RED", "GREEN")
        self.addTransition("slowdown", "GREEN", "YELLOW")
        self.addTransition("stop", "YELLOW", "init")

    def on_RED(self, msg='default', wait_time=6):
        logger.info("RED STATE: Stop! Received msg: %s" % msg)
        time.sleep(wait_time)

    def on_YELLOW(self, msg='default', wait_time=1):
        logger.info("YELLOW STATE: Slow down! Received msg: %s" % msg)
        time.sleep(wait_time)

    def on_GREEN(self, msg='default', wait_time=1):
        logger.info("GREEN STATE: Go! Received msg: %s" % msg)
        time.sleep(wait_time)

class Publisher(PyiCubRESTfulServer):

    def hello_world(self, name: str='you'):
        return "Hello world %s!" % name

app = Publisher()
fsm = Semaphore()
app.setFSM(fsm)

app.rest_manager.run_forever()
