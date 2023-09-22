# BSD 2-Clause License
#
# Copyright (c) 2022, Social Cognition in Human-Robot Interaction,
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

import json
from string import Template
from pyicub.utils import importFromJSONFile, exportJSONFile
from pyicub.controllers.position import JointPose, DEFAULT_TIMEOUT


class JointsTrajectoryCheckpoint:

    def __init__(self, pose: JointPose, duration: float=0.0, timeout: float=DEFAULT_TIMEOUT):
        self.pose = pose
        self.duration = duration
        self.timeout = timeout

    def toJSON(self):
        return self.__dict__


class LimbMotion:
    def __init__(self, part_name: str):
        self.part_name = part_name
        self.checkpoints = []

    def addCheckpoint(self, checkpoint: JointsTrajectoryCheckpoint):
        self.checkpoints.append(checkpoint)

    def toJSON(self):
        return self.__dict__

class PyiCubCustomCall:

    def __init__(self, target, args=()):
        self.target = target
        self.args = args

    def toJSON(self):
        return self.__dict__

class GazeMotion:
    def __init__(self, lookat_method: str):
        self.checkpoints = []
        self.lookat_method = lookat_method

    def addCheckpoint(self, value: list):
        self.checkpoints.append(value)

    def toJSON(self):
        return self.__dict__

class iCubFullbodyStep:

    def __init__(self, name='step', offset_ms=None):
        self.name = name
        self.limb_motions = {}
        self.gaze_motion = None
        self.custom_calls = []
        self.offset_ms = offset_ms

    def setGazeMotion(self, gaze_motion: GazeMotion):
        self.gaze_motion = gaze_motion

    def setLimbMotion(self, limb_motion: LimbMotion):
        self.limb_motions[limb_motion.part_name] = limb_motion

    def addCustomCall(self, custom_call: PyiCubCustomCall):
        self.custom_calls.append(custom_call)

    def toJSON(self):
        return self.__dict__


class iCubFullbodyAction:

    def __init__(self, name='action', description='empty', JSON_dict=None, offset_ms=None):
        self.steps = []
        self.name = name
        self.description = description
        self.offset_ms = offset_ms
        if JSON_dict:
            self.importFromJSONDict(JSON_dict)

    def addStep(self, step: iCubFullbodyStep):
        self.steps.append(step)

    def importFromJSONDict(self, json_dict):
        self.name = json_dict["name"]
        self.description = json_dict["description"]
        for step in json_dict["steps"]:
            res = iCubFullbodyStep(name=step["name"], offset_ms=step["offset_ms"])
            for part,pose in step["limb_motions"].items():
                lm = LimbMotion(part)
                for v in pose["checkpoints"]:
                    pose = JointPose(target_joints=v['pose']['target_joints'], joints_list=v['pose']['joints_list'])
                    check = JointsTrajectoryCheckpoint(pose, duration=v['duration'], timeout=v['timeout'])
                    lm.addCheckpoint(check)
                res.setLimbMotion(lm)
            if step["gaze_motion"]:
                gaze = GazeMotion(lookat_method=step["gaze_motion"]["lookat_method"])
                for v in step["gaze_motion"]["checkpoints"]:
                    gaze.addCheckpoint(v)
                res.setGazeMotion(gaze)
            if step["custom_calls"]:
                for v in step["custom_calls"]:
                    cc = PyiCubCustomCall(target=v["target"], args=v["args"])
                    res.addCustomCall(cc)
            self.addStep(res)

    def exportJSONFile(self, filepath):
        exportJSONFile(filepath, self)

    def toJSON(self):
        return self.__dict__

class TemplateParameter:

    def __init__(self, name: str, param_type: object):
        self.name = name
        self.param_type = str(param_type)
        self.key = '$' + self.name

    def setValue(self, value: object):
        self.value = value 

    def getValue(self):
        return self.value
        
    def toJSON(self):
        return {self.name: self.value}

    def exportJSONFile(self, filepath):
        exportJSONFile(filepath, self)

class iCubActionTemplate:

    def __init__(self, name='template'):
        self.name = name
        self.action = None
        self.parameters = {}            

    def __replace_params__(self, template_dict, params_dict):
        if isinstance(template_dict, dict):
            for key, value in template_dict.items():
                template_dict[key] = self.__replace_params__(value, params_dict)
        elif isinstance(template_dict, list):
            for i, item in enumerate(template_dict):
                template_dict[i] = self.__replace_params__(item, params_dict)
        elif isinstance(template_dict, str) and template_dict.startswith('$'):
            param_key = template_dict[1:]  # Remove the '$' character
            if param_key in params_dict:
                return params_dict[param_key]
        return template_dict

    def importFromJSONDict(self, JSON_dict, params_dict):
        self.name = JSON_dict['name']
        action_dict = self.__replace_params__(JSON_dict['action'], params_dict)
        self.action = iCubFullbodyAction(JSON_dict=action_dict)
        self.parameters = JSON_dict['parameters']
    
    def createParameter(self, name: str, param_type: object):
        param = TemplateParameter(name, param_type)
        self.parameters[name] = str(param_type)
        return param

    def getAction(self):
        return self.action

    def setAction(self, action: iCubFullbodyAction):
        self.action = action

    def exportJSONFile(self, filepath):
        exportJSONFile(filepath, self)

    def toJSON(self):
        return self.__dict__
