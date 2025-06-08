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

from pyicub.rest import iCubRESTApp, iCubFSM
from pyicub.actions import iCubFullbodyAction
import os


head_action = iCubFullbodyAction(JSON_file="actions/HeadAction.json")
lookat_action = iCubFullbodyAction(JSON_file="actions/LookAtAction.json")

class FSM_A(iCubFSM):

    def __init__(self):
        iCubFSM.__init__(self)
        lookat_state = self.addAction(lookat_action)
        self.addTransition("start", "init", lookat_state)
        self.exportJSONFile("FSM_A.json")
        self.draw("FSM_A.png")


class FSM_B(iCubFSM):

    def __init__(self):
        iCubFSM.__init__(self)
        head_state = self.addAction(head_action)
        lookat_state = self.addAction(lookat_action)
        self.addTransition("start", "init", head_state)
        self.addTransition("next", head_state, lookat_state)
        self.addTransition("reset", lookat_state, "init")
        self.exportJSONFile("FSM_B.json")
        self.draw("FSM_B.png")



class MultipleFSM(iCubRESTApp):

    def __init__(self, machine_id):
        self.FSM_A = FSM_A()
        self.FSM_B = FSM_B()
        iCubRESTApp.__init__(self, machine_id=machine_id)

    def configure(self, input_args):
        machine_id = int(input_args['machine_id'])

        if machine_id == 1:
            self.setFSM(self.FSM_A)
        elif machine_id == 2:
            self.setFSM(self.FSM_B)

app = MultipleFSM(machine_id=[1,2])
app.rest_manager.run_forever()