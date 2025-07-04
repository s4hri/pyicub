
# BSD 2-Clause License
#
# Copyright (c) 2025, Social Cognition in Human-Robot Interaction,
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


import yarp
from pyicub.core.rpc import RpcClient


class iLLM:
    """
    General interface to any YARP-based Large Language Model module.
    """

    def __init__(self, rpc_port_name="/LLM/rpc:i"):
        self.__rpcPort__ = RpcClient(rpc_port_name)

    def isValid(self):
        return self.__rpcPort__.connection_result

    def _send(self, command: str):
        btl = yarp.Bottle()
        btl.fromString(command)
        response = self.__rpcPort__.execute(btl)
        return response.toString()

    def status(self):
        return self._send("status")

    def query(self, text: str):
        return self._send(f'query {text}')

    def set_system_prompt(self, prompt: str):
        return self._send(f'set_system_prompt {prompt}')

    def create_session(self, session_id: str):
        return self._send(f'create_session {session_id}')

    def switch_session(self, session_id: str):
        return self._send(f'switch_session {session_id}')

    def reset_session(self, session_id: str):
        return self._send(f'reset_session {session_id}')

    def delete_session(self, session_id: str):
        return self._send(f'delete_session {session_id}')

    def list_sessions(self):
        return self._send('list_sessions')

    def set_model(self, model_name: str):
        return self._send(f'set_model {model_name}')

    def quit(self):
        return self._send('quit')
    


class iGPT(iLLM):
    """
    Specialized interface for the GPT YARP module.
    Uses /GPT/rpc:i as default port.
    """

    def __init__(self):
        super().__init__(rpc_port_name="/GPT/rpc:i")