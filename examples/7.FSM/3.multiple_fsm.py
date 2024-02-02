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

from pyicub.rest import iCubRESTApp
import os


class MultipleFSM(iCubRESTApp):

    def __init__(self, machine_id):
        iCubRESTApp.__init__(self, machine_id=machine_id)
        self.head_action = self.importAction("actions/HeadAction.json")
        self.lookat_action = self.importAction("actions/LookAtAction.json")

    
    def __configure__(self):
        machine_id = int(self.getArgs()['machine_id'])
        self.resetFSM()

        if machine_id == 1:
            self.fsm.addActionState(self.lookat_action)
            self.fsm.addTransition("start", "init", self.lookat_action)
            self.fsm.draw('3.M1_diagram.png')
        elif machine_id == 2:
            self.fsm.addActionState(self.head_action)
            self.fsm.addActionState(self.lookat_action)
            self.fsm.addTransition("start", "init", self.lookat_action)
            self.fsm.addTransition("next", self.lookat_action, self.head_action)
            self.fsm.addTransition("reset", self.head_action, "init")
            self.fsm.draw('3.M2_diagram.png')

app = MultipleFSM(machine_id=[1,2])
app.rest_manager.run_forever()