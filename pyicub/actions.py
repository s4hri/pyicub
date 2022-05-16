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
from pyicub.requests import iCubRequest

class JointPose:

    def __init__(self, target_joints, joints_list=None):
        self.target_joints = target_joints
        self.joints_list = joints_list

class JointsTrajectoryCheckpoint:

    def __init__(self, pose: JointPose, duration: float=0.0, timeout: float=0.0):
        self.pose = pose
        self.duration = duration
        self.timeout = timeout

class LimbMotion:
    def __init__(self, part_name: str):
        self.part_name = part_name
        self.checkpoints = []

    def addCheckpoint(self, checkpoint: JointsTrajectoryCheckpoint):
        self.checkpoints.append(checkpoint)

class PyiCubCustomCall:

    def __init__(self, target, args=(), timeout=iCubRequest.TIMEOUT_REQUEST):
        self.target = target
        self.args = args
        self.timeout = timeout

class GazeMotion:
    def __init__(self, lookat_method: str):
        self.checkpoints = []
        self.lookat_method = lookat_method

    def addCheckpoint(self, value: list):
        self.checkpoints.append(value)

class iCubFullbodyStep:

    def __init__(self, name='step', offset_ms=None, timeout=iCubRequest.TIMEOUT_REQUEST):
        self.name = name
        self.limb_motions = {}
        self.gaze_motion = None
        self.custom_calls = []
        self.offset_ms = offset_ms
        self.timeout = timeout

    def setGazeMotion(self, gaze_motion: GazeMotion):
        self.gaze_motion = gaze_motion

    def setLimbMotion(self, limb_motion: LimbMotion):
        self.limb_motions[limb_motion.part_name] = limb_motion

    def addCustomCall(self, custom_call: PyiCubCustomCall):
        self.custom_calls.append(custom_call)


class iCubFullbodyAction:

    def __init__(self, name='action', JSON_file=None):
        self.steps = []
        self.name = name
        if JSON_file:
            self.importFromJSONFile(JSON_file)
    
    def addStep(self, step: iCubFullbodyStep):
        self.steps.append(step)

    def fromJSON(self, json_dict):
        self.name = json_dict["name"]
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

    def importFromJSONFile(self, JSON_file):
        with open(JSON_file, encoding='UTF-8') as f:
            data = f.read()
        res = json.loads(data)
        self.fromJSON(res)

    def exportJSONFile(self, filepath):
        res = json.dumps(self, default=lambda o: o.__dict__, indent=4)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(res)
