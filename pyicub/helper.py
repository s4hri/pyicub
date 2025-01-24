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

import yarp
yarp.Network().init()

from pyicub.controllers.gaze import GazeController
from pyicub.controllers.position import PositionController, JointPose, iCubPart, ICUB_HEAD, ICUB_EYELIDS, ICUB_EYES, ICUB_NECK, ICUB_TORSO, ICUB_RIGHTARM_FULL, ICUB_LEFTARM_FULL, ICUB_RIGHTARM, ICUB_LEFTARM, ICUB_LEFTHAND, ICUB_RIGHTHAND
from pyicub.actions import PyiCubCustomCall, LimbMotion, GazeMotion, iCubFullbodyStep, iCubFullbodyAction, JointsTrajectoryCheckpoint, iCubActionTemplate, ActionsManager, TemplateParameter
from pyicub.modules.emotions import emotionsPyCtrl
from pyicub.modules.speech import iSpeakPyCtrl
from pyicub.modules.face import facePyCtrl
from pyicub.modules.faceLandmarks import faceLandmarksPyCtrl
from pyicub.modules.camera import cameraPyCtrl
from pyicub.core.ports import BufferedReadPort
from pyicub.core.logger import PyicubLogger, YarpLogger
from pyicub.requests import iCubRequest, iCubRequestsManager
from pyicub.utils import SingletonMeta, getPublicMethods, firstAvailablePort, importFromJSONFile, exportJSONFile
from collections import deque
from enum import Enum

import threading
import os
import time
import inspect



class iCubSingleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls.robot_name not in cls._instances.keys():
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls.robot_name] = instance
        return cls._instances[cls.robot_name]


class iCub(metaclass=iCubSingleton):

    def __init__(self, robot_name="icub", request_manager: iCubRequestsManager=None, action_repository_path='', proxy_host=None):
        SIMULATION = os.getenv('ICUB_SIMULATION')

        self._position_controllers_   = {}
        self._services_               = {}
        self._gaze_ctrl_              = None
        self._emo_                    = None
        self._speech_                 = None
        self._face_                   = None
        self._facelandmarks_          = None
        self._cam_right_              = None
        self._cam_left_               = None
        self._monitors_               = []
        self._logger_                 = YarpLogger.getLogger() #PyicubLogger.getLogger()
        self._request_manager_        = request_manager
        self._actions_manager_        = ActionsManager()
        self._action_repository_path_ = action_repository_path
        self._proxy_host_             = proxy_host

        self._icub_parts_                           = {}

        self._icub_parts_[ICUB_EYELIDS.name             ]   = ICUB_EYELIDS
        self._icub_parts_[ICUB_HEAD.name                ]   = ICUB_HEAD
        self._icub_parts_[ICUB_EYES.name                ]   = ICUB_EYES
        self._icub_parts_[ICUB_NECK.name                ]   = ICUB_NECK
        self._icub_parts_[ICUB_TORSO.name               ]   = ICUB_TORSO
        self._icub_parts_[ICUB_LEFTARM_FULL.name        ]   = ICUB_LEFTARM_FULL
        self._icub_parts_[ICUB_RIGHTARM_FULL.name       ]   = ICUB_RIGHTARM_FULL
        self._icub_parts_[ICUB_LEFTARM.name             ]   = ICUB_LEFTARM
        self._icub_parts_[ICUB_RIGHTARM.name            ]   = ICUB_RIGHTARM
        self._icub_parts_[ICUB_LEFTHAND.name            ]   = ICUB_LEFTHAND
        self._icub_parts_[ICUB_RIGHTHAND.name           ]   = ICUB_RIGHTHAND
        

        if SIMULATION:
            if SIMULATION == 'true':
                robot_name = "icubSim"

        self._robot_name_ = robot_name

        if action_repository_path:
            self.__importActions__(path=action_repository_path)

        self._initPositionControllers_()
        self._initGazeController_()

        if not self._request_manager_:
            self._request_manager_ = iCubRequestsManager(self._logger_)


    def __del__(self):
        print("Please Wait! Closing YARP connections...")
        self.close()
        yarp.Network().init()
        yarp.Network().fini()

    def __importActions__(self, path):
        json_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
        for f in json_files:
            self.importAction(os.path.join(path, f))
    
    def _initPositionControllers_(self):
        for part in self._icub_parts_.values():
            self._initPositionController_(part)

    def _initPositionController_(self, part: iCubPart):
        if part.name in self._position_controllers_.keys():
            return
        ctrl = PositionController(self._robot_name_, part, self._logger_)
        if ctrl.isValid():
            self._position_controllers_[part.name] = ctrl
            self._position_controllers_[part.name].init()
        else:
            self._logger_.warning('PositionController <%s> not callable! Are you sure the robot part is available?' % part.robot_part)

    def _initGazeController_(self):
        gaze_ctrl = GazeController(self._robot_name_, self._logger_)
        if gaze_ctrl.isValid():
            gaze_ctrl.init()
            self._gaze_ctrl_ = gaze_ctrl
        else:
            self._logger_.warning('GazeController not correctly initialized! Are you sure the controller is available?')
            self._gaze_ctrl_ = None

    def close(self):
        if len(self._monitors_) > 0:
            for v in self._monitors_:
                v.stop()
    @property
    def logger(self):
        return self._logger_

    @property
    def gaze(self):
        if self._gaze_ctrl_ is None:
            self._initGazeController_()
        return self._gaze_ctrl_

    @property
    def face(self):
        if self._face_ is None:
            try:
                self._face_ = facePyCtrl(self.robot_name)
            except:
                self._logger_.error('facePyCtrl not correctly initialized!')
                return None
        return self._face_

    @property
    def facelandmarks(self):
        if self._facelandmarks_ is None:
            try:
                self._facelandmarks_ = faceLandmarksPyCtrl()
            except:
                self._logger_.warning('facePyCtrl not correctly initialized!')
                return None
        return self._facelandmarks_

    @property
    def cam_right(self):
        if self._cam_right_ is None:
            try:
                self._cam_right_ = cameraPyCtrl(self._robot_name_, side="right", proxy_host=self._proxy_host_)
            except:
                self._logger_.warning('cameraPyCtrl (right) not correctly initialized!')
                return None
        return self._cam_right_

    @property
    def cam_left(self):
        if self._cam_left_ is None:
            try:
                self._cam_left_ = cameraPyCtrl(self._robot_name_, side="left", proxy_host=self._proxy_host_)
            except:
                self._logger_.warning('cameraPyCtrl (left) not correctly initialized!')
                return None
        return self._cam_left_

    @property
    def request_manager(self):
        return self._request_manager_

    @property
    def actions_manager(self):
        return self._actions_manager_

    @property
    def emo(self):
        if self._emo_ is None:
            self._emo_ = emotionsPyCtrl(self.robot_name)
        return self._emo_

    @property
    def speech(self):
        if self._speech_ is None:
            self._speech_ = iSpeakPyCtrl()
            if not self._speech_.isValid():
                self._logger_.error('iSpeakPyCtrl not correctly initialized!')
                self._speech_ = None
        return self._speech_

    @property
    def parts(self):
        return self._icub_parts_

    @property
    def robot_name(self):
        return self._robot_name_

    def addRuntimeModule(self, name, module):
        if not name in self.__dict__.keys(): 
            self.__dict__[name] = module
        else:
            self._logger_.error('You are trying to add a runtime module with a name %s that already exists in the helper class' % name)

    def addAction(self, action: iCubFullbodyAction, action_id=None):
        action_id = self.actions_manager.addAction(action, action_id=action_id)
        return action_id

    def exists(self):
        return len(self._position_controllers_.keys()) > 0

    def getPositionController(self, part: iCubPart):
        if part.name in self._position_controllers_.keys():
            return self._position_controllers_[part.name]
        self._logger_.error('PositionController <%s> non callable! Are you sure the robot part is available?' % part.name)
        return None
        
    def portmonitor(self, yarp_src_port, activate_function, callback):
        self._monitors_.append(PortMonitor(yarp_src_port, activate_function, callback, period=0.01, autostart=True))

    def execCustomCall(self, custom_call: PyiCubCustomCall, prefix='', ts_ref=0.0):
        calls = custom_call.target.split('.')
        foo = self
        for call in calls:
            foo = getattr(foo, call)
        req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST,
                                          target=foo, 
                                          name=prefix + '/%s' % str(custom_call.target), 
                                          ts_ref=ts_ref)
        self.request_manager.run_request(req, True, *custom_call.args)
        req.wait_for_completed()

    def execCustomCalls(self, calls, prefix='', ts_ref=0.0):
        for call in calls:
            self.execCustomCall(call, prefix, ts_ref)

    def exportAction(self, action_id: str, path):
        action = self.actions_manager.getAction(action_id)
        action.exportJSONFile('%s/%s.json' % (path, action_id))

    def getAction(self, action_id):
        return self.actions_manager.getAction(action_id)

    def getActions(self):
        return self.actions_manager.getActions()

    def importAction(self, JSON_file):
        return self.importActionFromJSONFile(JSON_file=JSON_file)

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

    def importActionFromTemplate(self, template: iCubActionTemplate, action_id=None):
        action = template.getAction()
        return self.actions_manager.addAction(action, action_id=action_id)

    def importTemplate(self, JSON_file):
        return self.actions_manager.importTemplateFromJSONFile(JSON_file=JSON_file)

    def movePart(self, limb_motion: LimbMotion, prefix='', ts_ref=0.0):
        requests = []
        ctrl = self.getPositionController(limb_motion.part)
        for i in range(0, len(limb_motion.checkpoints)):
            if ctrl is None:
                self._logger_.warning('movePart <%s> ignored!' % limb_motion.part.name)
            else:
                req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST, 
                                                  target=ctrl.move,
                                                  name=prefix + '/' + limb_motion.part.name,
                                                  ts_ref=ts_ref)

                self.request_manager.run_request(req,
                                                 wait_for_completed=True,
                                                 pose=limb_motion.checkpoints[i].pose,
                                                 req_time=limb_motion.checkpoints[i].duration,
                                                 timeout=limb_motion.checkpoints[i].timeout,
                                                 joints_speed=limb_motion.checkpoints[i].joints_speed,
                                                 tag=req.tag)
                
                requests.append(req)

        self.request_manager.join_requests(requests)       
        return requests


    def moveStep(self, step, prefix='', ts_ref=0.0):
        if ts_ref == 0.0:
            ts_ref = round(time.perf_counter(), 4)
        requests = []
        self._logger_.debug('Step <%s> STARTED!' % step.name)
        if step.offset_ms:
            time.sleep(step.offset_ms/1000.0)
        if step.gaze_motion:
            req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST,
                                              target=self.moveGaze,
                                              name=prefix + '/gaze',
                                              ts_ref=ts_ref)
            requests.append(req)
            self.request_manager.run_request(req,
                                             False,
                                             step.gaze_motion,
                                             req.tag,
                                             ts_ref)
        if step.custom_calls:
            req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST,
                                              target=self.execCustomCalls,
                                              name=prefix + '/custom',
                                              ts_ref=ts_ref)
            requests.append(req)
            self.request_manager.run_request(req,
                                             False,
                                             step.custom_calls,
                                             req.tag,
                                             ts_ref)
        for part, limb_motion in step.limb_motions.items():
            req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST,
                                              target=self.movePart,
                                              name=prefix + '/limb',
                                              ts_ref=ts_ref)
            requests.append(req)
            self.request_manager.run_request(req,
                                             False,
                                             limb_motion,
                                             req.tag,
                                             ts_ref)
        self.request_manager.join_requests(requests)
        self._logger_.debug('Step <%s> COMPLETED!' % step.name)
        return requests
    
    def moveSteps(self, steps, checkpoints, prefix, offset_ms=0.0):
        time.sleep(offset_ms/1000.0)
        requests = []
        t0 = round(time.perf_counter(), 4)
        for i in range(0, len(steps)):
            prefix = "%s/%s" % (prefix, steps[i].name)
            req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST,
                                              target=self.moveStep,
                                              name=prefix,
                                              ts_ref=t0)
            requests.append(req)
            self.request_manager.run_request(req,
                                             checkpoints[i],
                                             steps[i],
                                             req.tag,
                                             t0)
        self.request_manager.join_requests(requests)
        return requests


    def playAction(self, action_id: str, wait_for_completed=True, offset_ms=0.0):
        action = self.actions_manager.getAction(action_id)
        return self.runAction(action, wait_for_completed, offset_ms)

    def runAction(self, action: iCubFullbodyAction, wait_for_completed=True, offset_ms=0.0):
        t0 = round(time.perf_counter(), 4)
        self._logger_.debug('Playing action <%s>' % action.name)
        if action.offset_ms:
            offset_ms = action.offset_ms

        prefix = "/%s" % action.name
        req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST,
                                          target=self.moveSteps,
                                          name=prefix,
                                          ts_ref=t0)
        
        self.request_manager.run_request(req,
                                         wait_for_completed,
                                         action.steps,
                                         action.wait_for_steps,
                                         req.tag,
                                         offset_ms)
        if wait_for_completed:
            self._logger_.debug('Action <%s> finished!' % action.name)
        return req

    def moveGaze(self, gaze_motion: GazeMotion, prefix='', ts_ref=0.0):
        requests = []

        for i in range(0, len(gaze_motion.checkpoints)):
            req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST, 
                                              target=getattr(self.gaze, gaze_motion.lookat_method), 
                                              name=prefix + '/%s' % str(gaze_motion.lookat_method), 
                                              ts_ref=ts_ref)
            self.request_manager.run_request(req, True, *gaze_motion.checkpoints[i])
            requests.append(req)
        
        self.request_manager.join_requests(requests)

        return requests

class PortMonitor:
    def __init__(self, yarp_src_port, activate_function, callback, period=0.01, autostart=False):
        self._port_ = BufferedReadPort(yarp_src_port + "_reader_" + str(id(self)), yarp_src_port,)
        self._activate_ = activate_function
        self._callback_ = callback
        self._period_ = period
        self._values_ = deque( int(1000/(period*1000))*[None], maxlen=int(1000/(period*1000))) #Values of the last second
        self._stop_thread_ = False
        self._worker_thread_ = None
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
