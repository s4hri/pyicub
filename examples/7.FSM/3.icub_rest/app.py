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

app = iCubRESTApp(action_repository_path='./actions')

head_action = iCubFullbodyAction(JSON_file="actions/HeadAction.json")
lookat_action = iCubFullbodyAction(JSON_file="actions/LookAtAction.json")

fsm = iCubFSM(app=app)
head_state = fsm.addAction(action=head_action)
lookat_state = fsm.addAction(action=lookat_action)

fsm.addTransition("start", iCubFSM.INIT_STATE, head_state)
fsm.addTransition("next", head_state, lookat_state)
fsm.addTransition("reset", lookat_state, iCubFSM.INIT_STATE)

fsm.draw('diagram.png')
fsm.exportJSONFile('fsm.json')

app.setFSM(fsm)
app.rest_manager.run_forever()