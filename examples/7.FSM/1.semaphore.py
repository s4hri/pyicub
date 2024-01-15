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

class Semaphore(enum.Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2

def on_RED():
    print("Stop!")
    time.sleep(1)

def on_YELLOW():
    print("Slow down!")
    time.sleep(1)

def on_GREEN():
    print("Go!")
    time.sleep(1)

machine = FSM()

machine.addState(name=Semaphore.RED, on_enter_callback=on_RED)
machine.addState(name=Semaphore.YELLOW, on_enter_callback=on_YELLOW)
machine.addState(name=Semaphore.GREEN, on_enter_callback=on_GREEN)

machine.addTransition("start", "init", Semaphore.RED)
machine.addTransition("go", Semaphore.RED, Semaphore.GREEN)
machine.addTransition("slowdown", Semaphore.GREEN, Semaphore.YELLOW)
machine.addTransition("stop", Semaphore.YELLOW, Semaphore.RED)

triggers = machine.getCurrentTriggers()

for i in range(1,10):
    machine.runStep(triggers[0])
    triggers = machine.getCurrentTriggers()
    
print(machine.getStates())
print(machine.getTransitions())