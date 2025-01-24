# BSD 2-Clause License
#
# Copyright (c) 2023, Social Cognition in Human-Robot Interaction,
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

from pyicub.fsm import FSM
import enum
import time
import random
import logging

logger = logging.getLogger("fsm")

def on_RED(data):
    logger.info("Stop!")
    time.sleep(data)

def on_YELLOW(data):
    logger.info("Slow down!")
    time.sleep(data)

def on_GREEN(data):
    logger.info("Go!")
    time.sleep(data)

fsm = FSM("Semaphore")

fsm.addState(name="RED", on_enter_callback=on_RED)
fsm.addState(name="YELLOW", on_enter_callback=on_YELLOW)
fsm.addState(name="GREEN", on_enter_callback=on_GREEN)

# The initial state is always "init"
fsm.addTransition(trigger="start", source="init", dest="RED")
fsm.addTransition(trigger="go", source="RED", dest="GREEN")
fsm.addTransition(trigger="slowdown", source="GREEN", dest="YELLOW")
fsm.addTransition(trigger="stop", source="YELLOW", dest="init")

fsm.draw('diagram.png')

for i in range(3):
    triggers = ["start", "go", "slowdown", "stop"]
    for trigger in triggers:
        fsm.runStep(trigger, data=random.randrange(1,2))
    print("Session Count: ", fsm.getSessionCount())

print("\nSTATES: ", fsm.getStates())
print("\nTRANSITIONS: ", fsm.getTransitions())
print("\nFSM: ", fsm.toJSON())

fsm.exportJSONFile("fsm.json")


