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

from pyicub.helper import iCub, iCubActionTemplate

class TemplateExample(iCubActionTemplate):

    p1 = 1
    p2 = 2

    def prepare(self, p1, p2):
        self.addStep(p1)
        step2 = self.addStep()
        step2.setCustomCall(target="speech.say", args=("ciao",))

action = TemplateExample()
action.exportJSONFile("json/template.json")
#action_id = icub.addAction(action)
#icub.playAction(action_id)
#icub.exportAction(action_id=action_id, path=os.path.join(os.getcwd(), 'json'))


"""
template = iCubActionTemplate()
p1 = template.createParameter("step_bodymotion", iCubFullbodyStep)
p2 = template.createParameter("welcome_message", str)



action = iCubFullbodyAction()
action.addStep(p1.key)
speak = PyiCubCustomCall(target="speech.say", args=(p2.key,))
step = iCubFullbodyStep()
step.addCustomCall(speak)
action.addStep(step)

template.setAction(action)
template.exportJSONFile('json/hello.json')
"""