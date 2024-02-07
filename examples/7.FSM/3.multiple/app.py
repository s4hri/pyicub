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
import os


class FSM_A(iCubFSM):

    def __init__(self, app: iCubRESTApp):
        iCubFSM.__init__(self, app)
        action_id = "MultipleFSM.LookAtAction"
        self.addAction(action_id)
        self.addTransition("start", "init", action_id)
        self.exportJSONFile("FSM_A.json")
        self.draw('FSM_A.png')


class FSM_B(iCubFSM):

    def __init__(self, app: iCubRESTApp):
        iCubFSM.__init__(self, app)
        head_action = "MultipleFSM.HeadAction"
        lookat_action = "MultipleFSM.LookAtAction"

        self.addTransition("start", "init", head_action)
        self.addTransition("next", head_action, lookat_action)
        self.addTransition("reset", lookat_action, "init")
        self.exportJSONFile("FSM_B.json")
        self.draw('FSM_B.png')



class MultipleFSM(iCubRESTApp):

    def __init__(self, action_repository_path, machine_id):
        iCubRESTApp.__init__(self, action_repository_path=action_repository_path, machine_id=machine_id)

    def __configure__(self, input_args):
        machine_id = int(input_args['machine_id'])

        print("configure ", machine_id)

        if machine_id == 1:
            self.fsm.importFromJSONFile("FSM_A.json")
        elif machine_id == 2:
            self.fsm.importFromJSONFile("FSM_B.json")


app = MultipleFSM(action_repository_path='./actions', machine_id=[1,2])

FSM_A(app)
FSM_B(app)

app.rest_manager.run_forever()