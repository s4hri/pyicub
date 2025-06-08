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

from pyicub.rest import iCubRESTApp, iCubFSM
from pyicub.helper import iCubFullbodyStep, iCubFullbodyAction


class LookUp(iCubFullbodyStep):

    def prepare(self):
        g1 = self.createGazeMotion("lookAtFixationPoint")
        g1.addCheckpoint([-1.0, -0.5, 1.0])

class LookDown(iCubFullbodyStep):

    def prepare(self):
        g1 = self.createGazeMotion("lookAtFixationPoint")
        g1.addCheckpoint([-1.0, 0.2, 0.1])

class LookHome(iCubFullbodyStep):

    def prepare(self):
        g2 = self.createGazeMotion("lookAtAbsAngles")
        g2.addCheckpoint([0.0, 0.0, 0.0, True, 1.5])

class LookUpAction(iCubFullbodyAction):

    def prepare(self):
        self.addStep(LookUp())

class LookDownAction(iCubFullbodyAction):

    def prepare(self):
        self.addStep(LookDown())

class LookHomeAction(iCubFullbodyAction):
    def prepare(self):
        self.addStep(LookHome())



action_up = LookUpAction()
action_down = LookDownAction()
action_home = LookHomeAction()

fsm = iCubFSM()
lookup_state = fsm.addAction(action_up)
lookdown_state = fsm.addAction(action_down)
lookhome_state = fsm.addAction(action_home)

fsm.addTransition(iCubFSM.INIT_STATE, lookup_state)
fsm.addTransition(lookup_state, lookdown_state)
fsm.addTransition(lookdown_state, lookhome_state)
fsm.addTransition(lookhome_state, iCubFSM.INIT_STATE)

fsm.draw('diagram.png')
fsm.exportJSONFile('fsm.json')


class Publisher(iCubRESTApp):

    def __init__(self):
        self.myFSM = iCubFSM(JSON_file="fsm.json")
        iCubRESTApp.__init__(self)

    def configure(self, input_args):
        self.setFSM(self.myFSM)

app = Publisher()
app.rest_manager.run_forever()
