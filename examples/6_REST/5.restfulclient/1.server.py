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

from pyicub.rest import iCubRESTApp, iCub, rest_service
from datetime import date

import time
import os

class myRESTApp(iCubRESTApp):

    @rest_service
    def hello_world(self, name: str='you'):
        return "Hello world %s!" % name

    @rest_service
    def date(self, date_format: str="%d/%m/%Y"):
        today = date.today()
        return today.strftime(date_format)

    @rest_service
    def process(self):
        return "I am processing my arguments ... " + str(self.getArgs())

    @rest_service
    def foo(self):
        time.sleep(5)
        return "I've done a lot of stuff!"

icub = iCub()

template = icub.importTemplate(JSON_file="template/welcome.json")
template.setParam(JSON_file="template/params/msg1.json")
action1 = template.getAction(action_name="Welcome1")

template = icub.importTemplate(JSON_file="template/welcome.json")
template.setParam(JSON_file="template/params/msg2.json")
action2 = template.getAction(action_name="Welcome2")

app = iCubRESTApp()
app.importAction(action1)
app.importAction(action2)
app.rest_manager.run_forever()



