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
from pyicub.modules.llm import iGPT

# Initialize YARP network
yarp.Network.init()

# Create iGPT client
gpt = iGPT()

# Check connection
if not gpt.isValid():
    print("[ERROR] Could not connect to /GPT/rpc:i")
    exit(1)

# Show module status
print("Module status:", gpt.status())

# Create and switch to a new session
print("Creating session 'test1'")
print(gpt.create_session("test1"))

print("Switching to session 'test1'")
print(gpt.switch_session("test1"))

# Set a custom system prompt
prompt = "You are a wise assistant who answers briefly and accurately."
print("Setting system prompt:")
print(gpt.set_system_prompt(prompt))

# Run a test query
print("Querying: 'What is the capital of Italy?'")
response = gpt.query("What is the capital of Italy?")
print("Response:", response)

# List current sessions
print("Active sessions:", gpt.list_sessions())

# Finish YARP
yarp.Network.fini()
