#   Copyright (C) 2021  Davide De Tommaso
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>

import yarp
yarp.Network.init()

from pyicub.controllers.gaze import GazeMotion, GazeController
from pyicub.controllers.position import JointPose, JointsTrajectoryCheckpoint, LimbMotion, ICUB_PARTS, iCubPart, PositionController
from pyicub.modules.emotions import emotionsPyCtrl
from pyicub.modules.speech import speechPyCtrl
from pyicub.modules.face import facePyCtrl
from pyicub.modules.faceLandmarks import faceLandmarksPyCtrl
from pyicub.core.ports import BufferedReadPort
from pyicub.core.logger import YarpLogger
from pyicub.requests import iCubRequestsManager, iCubRequest

from collections import deque
import threading
import yaml
import os
import time
import json


class PortMonitor:
    def __init__(self, yarp_src_port, activate_function, callback, period=0.01, autostart=False):
        self._port_ = BufferedReadPort(yarp_src_port + "_reader_" + str(id(self)), yarp_src_port,)
        self._activate_ = activate_function
        self._callback_ = callback
        self._period_ = period
        self._values_ = deque( int(1000/(period*1000))*[None], maxlen=int(1000/(period*1000))) #Values of the last second
        self._stop_thread_ = False
        if autostart:
            self.start()

    def start(self):
        if self._stop_thread_:
           self.stop()
        self._worker_thread_ = threading.Thread(target=self.worker)
        self._worker_thread_.start()

    def stop(self):
        if not self._stop_thread_:
            self._stop_thread_ = True
        self._worker_thread_.join()
        self._stop_thread_ = False

    def worker(self):
        while not self._stop_thread_:
            res = self._port_.read(shouldWait=False)
            if not res is None:
                self._values_.append(res.toString())
                if self._activate_(self._values_):
                    self._callback_()
            yarp.delay(self._period_)

    def __del__(self):
        self.stop()
        del self._port_

class PyiCubCustomCall:

    def __init__(self, target, args=()):
        self.target = target
        self.args = args

class iCubFullbodyStep:

    def __init__(self):
        self.limb_motions = {}
        self.gaze_motion = None
        self.custom_calls = []

    def setGazeMotion(self, gaze_motion: GazeMotion):
        self.gaze_motion = gaze_motion

    def setLimbMotion(self, limb_motion: LimbMotion):
        self.limb_motions[limb_motion.part_name] = limb_motion

    def addCustomCall(self, custom_call: PyiCubCustomCall):
        self.custom_calls.append(custom_call)


class iCubFullbodyAction:

    def __init__(self, JSON_file=None):
        self.steps = []
        if JSON_file:
            self.importJSON(JSON_file)

    def addStep(self):
        step = iCubFullbodyStep()
        self.steps.append(step)
        return step

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def fromJSON(self, json_obj):
        j = json.loads(json_obj)
        for step in j["steps"]:
            res = self.addStep()
            for part,pose in step["limb_motions"].items():
                lm = LimbMotion(part)
                for v in pose["checkpoints"]:
                    pose = JointPose(target_joints=v['pose']['target_joints'], joints_list=v['pose']['joints_list'])
                    check = JointsTrajectoryCheckpoint(pose, duration=v['duration'])
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

    def importJSON(self, JSON_file):
        with open(JSON_file) as f:
            data = f.read()
        self.fromJSON(data)


    def exportJSON(self, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.toJSON())

class iCub:

    def __init__(self, configuration_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'robot_configuration.yaml'), disable_logs=False, http_server=False):
        self._icub_controllers_ = {}
        self._position_controllers_ = {}
        self._drivers_ = {}
        self._encoders_ = {}
        self._gaze_ctrl_ = None
        self._emo_ = None
        self._speech_ = None
        self._face_ = None
        self._facelandmarks_ = None
        self._monitors_ = []
        self._logger_ = YarpLogger.getLogger()

        if disable_logs:
            self._logger_.disable_logs()

        if http_server:
            self._http_manager_ = iCubHTTPManager()
        else:
            self._http_manager_ = None

        self._icub_parts_ = {}
        self._icub_parts_[ICUB_PARTS.HEAD] = iCubPart(ICUB_PARTS.HEAD, 6)
        self._icub_parts_[ICUB_PARTS.FACE] = iCubPart(ICUB_PARTS.FACE, 1)
        self._icub_parts_[ICUB_PARTS.LEFT_ARM] = iCubPart(ICUB_PARTS.LEFT_ARM, 16)
        self._icub_parts_[ICUB_PARTS.RIGHT_ARM] = iCubPart(ICUB_PARTS.RIGHT_ARM, 16)
        self._icub_parts_[ICUB_PARTS.TORSO] = iCubPart(ICUB_PARTS.TORSO, 3)
        self._icub_parts_[ICUB_PARTS.LEFT_LEG] = iCubPart(ICUB_PARTS.LEFT_LEG, 6)
        self._icub_parts_[ICUB_PARTS.RIGHT_LEG] = iCubPart(ICUB_PARTS.RIGHT_LEG, 6)

        with open(configuration_file) as f:
            self._robot_conf_ = yaml.load(f, Loader=yaml.FullLoader)

        self._robot_ = self._robot_conf_['robot_name']

        if 'gaze_controller' in self._robot_conf_.keys():
            if self._robot_conf_['gaze_controller'] is True:
                self._gaze_ctrl_ = GazeController(self._robot_)

        if 'position_controllers' in self._robot_conf_.keys():
            for part_name in self._robot_conf_['position_controllers']:
                self._icub_controllers_[part_name] = self.getPositionController(self._icub_parts_[part_name])

        if self._http_manager_:
            self._registerDefaultServices_()

    def _getDriver_(self, robot_part):
        if not robot_part.name in self._drivers_.keys():
            props = self._getRobotPartProperties_(robot_part)
            self._drivers_[robot_part.name] = yarp.PolyDriver(props)
        return self._drivers_[robot_part.name]

    def _getIEncoders_(self, robot_part):
        if not robot_part.name in self._encoders_.keys():
            driver = self._getDriver_(robot_part)
            self._encoders_[robot_part.name] = driver.viewIEncoders()
        return self._encoders_[robot_part.name]

    def _getRobotPartProperties_(self, robot_part):
        props = yarp.Property()
        props.put("device","remote_controlboard")
        props.put("local","/client/" + self._robot_ + "/" + robot_part.name)
        props.put("remote","/" + self._robot_ + "/" + robot_part.name)
        return props

    def _registerDefaultServices_(self):
        if self.gaze:
            self.http_manager.register(self.gaze.blockEyes, rule_prefix="gaze_controller")
            self.http_manager.register(self.gaze.blockNeck, rule_prefix="gaze_controller")
            self.http_manager.register(self.gaze.clearEyes, rule_prefix="gaze_controller")
            self.http_manager.register(self.gaze.clearNeck, rule_prefix="gaze_controller")
            self.http_manager.register(self.gaze.lookAtAbsAngles, rule_prefix="gaze_controller")
            self.http_manager.register(self.gaze.lookAtFixationPoint, rule_prefix="gaze_controller")
            self.http_manager.register(self.gaze.reset, rule_prefix="gaze_controller")
            self.http_manager.register(self.gaze.setParams, rule_prefix="gaze_controller")
            self.http_manager.register(self.gaze.setTrackingMode, rule_prefix="gaze_controller")


    def close(self):
        if len(self._monitors_) > 0:
            for v in self._monitors_:
                v.stop()
        for driver in self._drivers_.values():
            driver.close()
        yarp.Network.fini()


    @property
    def gaze(self):
        if self._gaze_ctrl_ is None:
            self._gaze_ctrl_ = GazeController(self._robot_)
        return self._gaze_ctrl_

    @property
    def face(self):
        if self._face_ is None:
            self._face_ = facePyCtrl(self._robot_)
        return self._face_

    @property
    def facelandmarks(self):
        if self._facelandmarks_ is None:
           self._facelandmarks_ = faceLandmarksPyCtrl()
        return self._facelandmarks_

    @property
    def http_manager(self):
        return self._http_manager_

    @property
    def emo(self):
        if self._emo_ is None:
            self._emo_ = emotionsPyCtrl(self._robot_)
        return self._emo_

    @property
    def speech(self):
        if self._speech_ is None:
            self._speech_ = speechPyCtrl(self._robot_)
        return self._speech_

    def portmonitor(self, yarp_src_port, activate_function, callback):
        self._monitors_.append(PortMonitor(yarp_src_port, activate_function, callback, period=0.01, autostart=True))

    def getPositionController(self, robot_part, joints_list=None):
        if not robot_part in self._position_controllers_.keys():
            driver = self._getDriver_(robot_part)
            iencoders = self._getIEncoders_(robot_part)
            if joints_list is None:
                joints_list = robot_part.joints_list
            self._position_controllers_[robot_part.name] = PositionController(driver, joints_list, iencoders)
        return self._position_controllers_[robot_part.name]

    def execCustomCall(self, custom_call: PyiCubCustomCall):
        calls = custom_call.target.split('.')
        foo = self
        for call in calls:
            foo = getattr(foo, call)
        req = iCubRequestsManager().create(timeout=iCubRequest.TIMEOUT_REQUEST, target=foo)
        req.run(*custom_call.args)
        req.wait_for_completed()

    def moveGaze(self, gaze_motion: GazeMotion):
        for i in range(0, len(gaze_motion.checkpoints)):
            req = iCubRequestsManager().create(timeout=iCubRequest.TIMEOUT_REQUEST, target=getattr(self.gaze, gaze_motion.lookat_method))
            req.run(gaze_motion.checkpoints[i][0], gaze_motion.checkpoints[i][1], gaze_motion.checkpoints[i][2])
            req.wait_for_completed()

    def movePart(self, limb_motion: LimbMotion):
        for i in range(0, len(limb_motion.checkpoints)):
            part_name = limb_motion.part_name
            ctrl = self._icub_controllers_[part_name]
            duration = limb_motion.checkpoints[i].duration
            req = iCubRequestsManager().create(timeout=iCubRequest.TIMEOUT_REQUEST, target=ctrl.move)
            req.run(pose=limb_motion.checkpoints[i].pose, req_time=limb_motion.checkpoints[i].duration)
            req.wait_for_completed()

    def execCustomCalls(self, calls):
        for call in calls:
            self.execCustomCall(call)

    def moveStep(self, step):
        requests = []
        if step.gaze_motion:
            req = iCubRequestsManager().create(timeout=iCubRequest.TIMEOUT_REQUEST, target=self.moveGaze)
            requests.append(req)
            req.run(step.gaze_motion)
        if step.custom_calls:
            req = iCubRequestsManager().create(timeout=iCubRequest.TIMEOUT_REQUEST, target=self.execCustomCalls)
            requests.append(req)
            req.run(step.custom_calls)
        for part, limb_motion in step.limb_motions.items():
            req = iCubRequestsManager().create(timeout=iCubRequest.TIMEOUT_REQUEST, target=self.movePart)
            requests.append(req)
            req.run(limb_motion)

        return requests

    def play(self, action: iCubFullbodyAction):
        for step in action.steps:
            requests = self.moveStep(step)
            iCubRequest.join(requests)
