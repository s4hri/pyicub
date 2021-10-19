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

from pyicub.controllers.GazeController import GazeController
from pyicub.controllers.PositionController import PositionController
from pyicub.modules.emotions import emotionsPyCtrl
from pyicub.modules.speech import speechPyCtrl
from pyicub.modules.face import facePyCtrl
from pyicub.modules.faceLandmarks import faceLandmarksPyCtrl
from pyicub.core.BufferedPort import BufferedReadPort
from pyicub.core.Logger import YarpLogger

import threading
import yaml
import os
import time
from collections import deque
import concurrent.futures

from flask import Flask, jsonify, request

class ICUB_PARTS:
    HEAD       = 'head'
    FACE       = 'face'
    TORSO      = 'torso'
    LEFT_ARM   = 'left_arm'
    RIGHT_ARM  = 'right_arm'
    LEFT_LEG   = 'left_leg'
    RIGHT_LEG  = 'right_leg'

class iCubPart:
    def __init__(self, name, joints_n):
        self.name = name
        self.joints_n = joints_n
        self.joints_list = range(0, joints_n)

class JointPose:
    def __init__(self, part_name, target_position, joints_list=None):
        self.part_name = part_name
        self.target_position = target_position
        self.joints_list = joints_list

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

class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class iCubRequest:

    INIT    = 'INIT'
    RUNNING = 'RUNNING'
    TIMEOUT = 'TIMEOUT'
    DONE    = 'DONE'
    FAILED  = 'FAILED'

    TIMEOUT_REQUEST = 30.0

    def __init__(self, req_id, timeout, target):
        self._start_time_ = time.perf_counter()
        self._end_time_ = None
        self._req_id_ = req_id
        self._status_ = iCubRequest.INIT
        self._timeout_ = timeout
        self._duration_ = None
        self._exception_ = None
        self._executor_ = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._target_ = target
        self._retval_ = None

    @property
    def duration(self):
        return self._duration_

    @property
    def end_time(self):
        return self._end_time_

    @property
    def exception(self):
        return self._exception_

    @property
    def req_id(self):
        return self._req_id_

    @property
    def retval(self):
        return self._retval_

    @property
    def status(self):
        return self._status_

    @property
    def start_time(self):
        return self._start_time_

    @property
    def target(self):
        return self._target_


    def run(self, *args, **kwargs):
        self._future_ = self._executor_.submit(self._target_, *args, **kwargs)
        self._future_.add_done_callback(self.on_completed)
        self._status_ = iCubRequest.RUNNING

    def on_completed(self, future):
        self._end_time_ = time.perf_counter()
        self._duration_ = self._end_time_ - self._start_time_
        self._status_ = iCubRequest.DONE

    def wait_for_completed(self):
        res = None
        try:
            res = self._future_.result(self._timeout_)
        except Exception as e:
            self._end_time_ = time.perf_counter()
            self._duration_ = self._end_time_ - self._start_time_
            self._status_ = iCubRequest.FAILED
            self._exception_ = str(e)
        finally:
            self._executor_.shutdown(wait=False)
        self._retval_ = res
        return res

class iCubRequestsManager(metaclass=SingletonMeta):

    def __init__(self):
        self._requests_ = {}

    def create(self, timeout, target):
        if len(self._requests_) == 0:
            req_id = 0
        else:
            req_id = max(self._requests_.keys()) + 1
        req = iCubRequest(req_id, timeout, target)
        self._requests_[req_id] = req
        return req

    def run(self, req_id, *args, **kwargs):
        self._requests_[req_id].run(*args, **kwargs)
        threading.Thread(target=self._requests_[req_id].wait_for_completed).start()
        return self.info(req_id)

    def info(self, req_id):
        info = {}
        req_id = int(req_id)
        info['target'] = self._requests_[req_id].target.__name__
        info['id'] = self._requests_[req_id].req_id
        info['status'] = self._requests_[req_id].status
        info['start_time'] = self._requests_[req_id].start_time
        info['end_time'] = self._requests_[req_id].end_time
        info['duration'] = self._requests_[req_id].duration
        info['exception'] = self._requests_[req_id].exception
        info['retval'] = self._requests_[req_id].retval
        return info


class iCubHTTPManager(iCubRequestsManager):

    def __init__(self, rule_prefix="/pyicub", host=None, port=None):
        iCubRequestsManager.__init__(self)
        self._services_ = {}
        self._flaskapp_ = Flask(__name__)
        self._rule_prefix_ = rule_prefix
        self._flaskapp_.add_url_rule(self._rule_prefix_, methods=['GET'], view_func=self.list)
        threading.Thread(target=self._flaskapp_.run, args=(host, port,)).start()

    def shutdown(self):
        print("SHOO")
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def wrapper_target(self, *args, **kwargs):
        rule = str(request.url_rule).strip()
        if request.method == 'GET':
            name = self._services_[rule].__name__
            res = []
            for req_id, req in self._requests_.items():
                if req.target.__name__ == name:
                    res.append(self.info(req_id))
            return jsonify(res)
        elif request.method == 'POST':
            req = self.create(iCubRequest.TIMEOUT_REQUEST, self._services_[rule])
            self._requests_[req.req_id] = req
            res = request.get_json(force=True)
            args = tuple(res.values())
            kwargs =  res
            self.run(req.req_id, **kwargs)
            return jsonify(req.req_id)

    def wrapper_info(self, req_id):
        return self.info(req_id)

    def list(self):
        return jsonify(list(self._services_.keys()))

    def register(self, target, rule_prefix=None):
        if rule_prefix:
            rule = "%s/%s/%s" % (self._rule_prefix_, rule_prefix, target.__name__)
        else:
            rule = "%s/%s" % (self._rule_prefix_, target.__name__)
        self._flaskapp_.add_url_rule(rule, methods=['GET', 'POST'], view_func=self.wrapper_target)
        self._services_[rule] = target
        self._flaskapp_.add_url_rule("%s/<req_id>" % rule, methods=['GET'], view_func=self.wrapper_info)



class iCubTask:

    @staticmethod
    def request(timeout=iCubRequest.TIMEOUT_REQUEST):
        def wrapper(target):
                def f(*args, **kwargs):
                    req = iCubRequestsManager().create(timeout, target)
                    return req.run(*args, **kwargs)
                return f
        return wrapper

    @staticmethod
    def join(requests):
        for req in requests:
            req.wait_for_completed()

class iCub:

    def __init__(self, configuration_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'robot_configuration.yaml'), disable_logs=False, http_server=False):
        self._icub_controllers_ = {}
        self._position_controllers_ = {}
        self._drivers_ = {}
        self._encoders_ = {}
        self._gazectrl_ = None
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
                self._gazectrl_ = GazeController(self._robot_)

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
    def gaze(self):
        return self._gazectrl_

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

    def move(self, pose, req_time, in_parallel=False, vel_list=None):
        ctrl = self._icub_controllers_[pose.part_name]

        if in_parallel is True:
            if vel_list is None:
                return iCubRequestsManager().create(timeout=iCubRequest.TIMEOUT_REQUEST, target=ctrl.move, target_joints=pose.target_position, req_time=req_time, joints_list=pose.joints_list)
            else:
                return iCubRequestsManager().create(timeout=iCubRequest.TIMEOUT_REQUEST, target=ctrl.moveRefVel, target_joints=pose.target_position, req_time=req_time, joints_list=pose.joints_list, vel_list=vel_list)
        else:
            if vel_list is None:
                return ctrl.move(target_joints=pose.target_position, req_time=req_time, joints_list=pose.joints_list)
            else:
                return ctrl.moveRefVel(target_joints=pose.target_position, req_time=req_time, joints_list=pose.joints_list, vel_list=vel_list)
