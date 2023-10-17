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

    def createJointsTrajectory(self, pose: JointPose, duration: float=0.0, timeout: float=DEFAULT_TIMEOUT):
        checkpoint = JointsTrajectoryCheckpoint(pose=pose, duration=duration, timeout=timeout)
        self.checkpoints.append(checkpoint)
        return checkpoint

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

    def __init__(self, offset_ms=None, name=None, JSON_dict=None, JSON_file=None):
        if not name:
            self.name = self.__class__.__name__
        self.limb_motions = {}
        self.gaze_motion = None
        self.custom_calls = []
        self.offset_ms = offset_ms
        if JSON_dict or JSON_file:
            if JSON_dict:
                self.importFromJSONDict(JSON_dict)
            else:
                self.importFromJSONFile(JSON_file)
        else:
            self.prepare()

    def prepare(self):
        raise NotImplementedError("The method 'prepare' contains definition for creating custom iCubFullbodyStep.")

    def createCustomCall(self, target, args=()):
        cc = PyiCubCustomCall(target=target, args=args)
        self.setCustomCall(cc)
        return cc

    def createGazeMotion(self, lookat_method: str):
        gm = GazeMotion(lookat_method)
        self.setGazeMotion(gm)
        return gm

    def createLimbMotion(self, part_name: str):
        lm = LimbMotion(part_name)
        self.setLimbMotion(lm)
        return lm

    def exportJSONFile(self, filepath):
        exportJSONFile(filepath, self)

    def setLimbMotion(self, limb_motion: LimbMotion):
        self.limb_motions[limb_motion.part_name] = limb_motion

    def setCustomCall(self, custom_call: PyiCubCustomCall):
        self.custom_calls.append(custom_call)

    def setGazeMotion(self, gaze_motion: GazeMotion):
        self.gaze_motion = gaze_motion

    def importFromJSONDict(self, json_dict):
        self.name = json_dict["name"]
        self.offset_ms = json_dict["offset_ms"]
        for part,pose in json_dict["limb_motions"].items():
            lm = self.createLimbMotion(part)
            for v in pose["checkpoints"]:
                pose = JointPose(target_joints=v['pose']['target_joints'], joints_list=v['pose']['joints_list'])
                lm.createJointsTrajectory(pose, duration=v['duration'], timeout=v['timeout'])
        if json_dict["gaze_motion"]:
            gaze = self.createGazeMotion(lookat_method=json_dict["gaze_motion"]["lookat_method"])
            for v in json_dict["gaze_motion"]["checkpoints"]:
                gaze.addCheckpoint(v)
        if json_dict["custom_calls"]:
            for v in json_dict["custom_calls"]:
                self.createCustomCall(target=v["target"], args=v["args"])

    def importFromJSONFile(self, JSON_file):
        JSON_dict = importFromJSONFile(JSON_file)
        self.importFromJSONDict(JSON_dict)

    def toJSON(self):
        return self.__dict__


class iCubFullbodyAction:

    def __init__(self, description='empty', name=None, offset_ms=None, JSON_dict=None, JSON_file=None):
        self.steps = []
        if not name:
            self.name = self.__class__.__name__
        self.description = description
        self.offset_ms = offset_ms
        if JSON_dict or JSON_file:
            if JSON_dict:
                self.importFromJSONDict(JSON_dict)
            else:
                self.importFromJSONFile(JSON_file)
        else:
            self.prepare()

    def prepare(self):
        raise NotImplementedError("The method 'prepare' contains definition for creating custom actions.")

    def addStep(self, step: iCubFullbodyStep):
        self.steps.append(step)

    def importFromJSONDict(self, json_dict):
        self.name = json_dict["name"]
        self.offset_ms = json_dict["offset_ms"]
        self.description = json_dict["description"]
        for step in json_dict["steps"]:
            res = iCubFullbodyStep(JSON_dict=step)
            self.addStep(res)

    def importFromJSONFile(self, JSON_file):
        JSON_dict = importFromJSONFile(JSON_file)
        self.importFromJSONDict(JSON_dict)

    def exportJSONFile(self, filepath):
        exportJSONFile(filepath, self)

    def setName(self, name):
        self.name = name

    def setDescription(self, description):
        self.description = description

    def setOffset(self, offset_ms):
        self.offset_ms = offset_ms

    def toJSON(self):
        return self.__dict__
                    

class iCubActionTemplate(iCubFullbodyAction):

    def __init__(self, description='empty', name=None, offset_ms=None):
        self.params = {}
        self.prepare_params()
        iCubFullbodyAction.__init__(self, description=description, name=name, offset_ms=offset_ms)

    def prepare_params(self):
        raise NotImplementedError("The method 'prepare_params' contains definition for creating custom actions.")
            
    def createParam(self, name):
        self.params[name] = '$' + name

    def getParams(self):
        return self.params

    def getParam(self, name):
        return self.params[name]
    
    def setParams(self, params):
        self.params = params

    def setParam(self, name, value=None, JSON_file=None):
        if JSON_file:
            value = importFromJSONFile(JSON_file)[name]
        self.params[name] = value

class iCubActionTemplateImportedJSON(iCubActionTemplate):

    def __init__(self, JSON_dict):
        self._json_dict_ = JSON_dict
        self.name = JSON_dict['name']
        iCubActionTemplate.__init__(self, description=JSON_dict["description"], name=JSON_dict["name"], offset_ms=JSON_dict["offset_ms"])

    def prepare_params(self):
        for k in self._json_dict_['params'].keys():
            self.createParam(name=k)

    def prepare(self):
        pass

    def getActionDict(self):
        return self.__replace_params__(self._json_dict_, self.params)

    def getAction(self, action_name=None):
        action_dict = self.getActionDict()
        action = iCubFullbodyAction(JSON_dict=action_dict)
        action.setName(action_name)
        return action

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

    

class ActionsManager:

    def __init__(self):
        self.__actions__ = {}

    def addAction(self, action: iCubFullbodyAction, action_id=None):
        if not action_id:
            action_id = action.name
        if action_id in self.__actions__.keys():
            raise Exception("An error occurred adding a new action! Class name '%s' already present! Please choose different names for each class actions." % action_id)
        self.__actions__[action_id] = action
        return action_id

    def getAction(self, action_id: str):
        if action_id in self.__actions__.keys():
            return self.__actions__[action_id]
        raise Exception("action_id '%s' not found! Please provide an action identifier previously imported!" % action_id)

    def getActions(self):
        return self.__actions__.keys()

    def exportActions(self, path):
        for k, action in self.__actions__.items():
            action.exportJSONFile('%s/%s.json' % (path, k))

    def importActionFromJSONDict(self, JSON_dict, name_prefix=None):
        action = iCubFullbodyAction(JSON_dict=JSON_dict)
        if name_prefix:
            action_id=name_prefix + '.' + action.name
        else:
            action_id=None
        return self.addAction(action, action_id=action_id)

    def importActionFromJSONFile(self, JSON_file):
        JSON_dict = importFromJSONFile(JSON_file)
        return self.importActionFromJSONDict(JSON_dict=JSON_dict)

    def importTemplateFromJSONFile(self, JSON_file):
        JSON_dict = importFromJSONFile(JSON_file)
        return self.importTemplateFromJSONDict(JSON_dict=JSON_dict)

    def importTemplateFromJSONDict(self, JSON_dict):
        return iCubActionTemplateImportedJSON(JSON_dict=JSON_dict)

    def importActionFromTemplateJSONFile(self, JSON_file, params_files=[]):
        template_dict = importFromJSONFile(JSON_file)
        params_dict = {}
        for j in params_files:
            param = importFromJSONFile(j)
            params_dict.update(param)
        return self.importActionFromTemplateJSONDict(template_dict, params_dict)

    def importTemplateJSONFile(self, JSON_file):
        return importFromJSONFile(JSON_file)
