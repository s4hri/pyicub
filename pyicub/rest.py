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

from pyicub.requests import iCubRequest
from pyicub.utils import SingletonMeta, getPyiCubInfo, getPublicMethods, firstAvailablePort, importFromJSONFile
from pyicub.core.logger import PyicubLogger, YarpLogger
from pyicub.requests import iCubRequestsManager, iCubRequest
from pyicub.helper import iCub
from flask import Flask, jsonify, request

import requests
import json
import time
import os
import inspect


class iCubRESTService:

    def __init__(self, name, robot_name, app_name, url, target, signature):

        self.name = name
        self.robot_name = robot_name
        self.app_name = app_name
        self.url = url
        self.target = target
        self.signature = signature


class iCubRESTServer(metaclass=SingletonMeta):

    def __init__(self, rule_prefix, host, port):
        self._services_ = {}
        self._app_services_ = {}
        self._apps_ = {}
        self._robots_ = {}
        self._flaskapp_ = Flask(__name__)
        self._host_ = host
        self._port_ = port
        self._rule_prefix_ = rule_prefix
        self._flaskapp_.add_url_rule("/", methods=['GET'], view_func=self.info)
        self._flaskapp_.add_url_rule("/%s" % self._rule_prefix_, methods=['GET'], view_func=self.list_robots)
        self._flaskapp_.add_url_rule("/%s/tree" % self._rule_prefix_, methods=['GET'], view_func=self.get_tree)
        self._flaskapp_.add_url_rule("/%s/register" % self._rule_prefix_, methods=['POST'], view_func=self.remote_register)
        self._flaskapp_.add_url_rule("/%s/unregister" % self._rule_prefix_, methods=['POST'], view_func=self.remote_unregister)

        self._flaskapp_.add_url_rule("/%s/<robot_name>" % self._rule_prefix_, methods=['GET'], view_func=self.list_apps)
        self._flaskapp_.add_url_rule("/%s/<robot_name>/<app_name>" % self._rule_prefix_, methods=['GET'], view_func=self.list_services)
        self._flaskapp_.add_url_rule("/%s/<robot_name>/<app_name>/<target_name>" % (self._rule_prefix_), methods=['GET', 'POST'], view_func=self.wrapper_target)

    def header(self, host, port):
        return "http://%s:%s" % (host, port)
    
    def server_rule(self, host=None, port=None):
        if host and port:
            header = self.header(host, port)
        else:
            header = self.header(self._host_, self._port_)
        return header + '/' + self._rule_prefix_
        
    def robot_rule(self, robot_name, host=None, port=None):
        return self.server_rule(host, port) + "/" + robot_name

    def app_rule(self, robot_name, app_name, host=None, port=None):
        return self.robot_rule(robot_name, host, port) + "/" + app_name

    def target_rule(self, robot_name, app_name, target_name, host=None, port=None):
        return self.app_rule(robot_name, app_name, host, port) + "/" + target_name

    def run_forever(self):
        stop = False
        while not stop:
            try:
                self._flaskapp_.run(self._host_, self._port_)
                stop = True
            except:
                self._port_ += 1
     
    def shutdown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()


    def wrapper_target(self, robot_name, app_name, target_name):
        target_rule = self.target_rule(robot_name, app_name, target_name)
        if request.method == 'GET':
            return json.dumps(self._services_[target_rule], default=lambda o: o.__dict__, indent=4)
        elif request.method == 'POST':
            if self._services_[target_rule].target:
                return self.process_target(self._services_[target_rule])
            return self.process_target_remote(self._services_[target_rule])

    def process_target_remote(self, service):
        url = service.url
        data = request.get_json(force=True)
        if 'sync' in request.args:
            url+="?sync"
        res = requests.post(url=url, json=data)
        return res.content

    def info(self):
        return jsonify(getPyiCubInfo())

    def get_tree(self):
        return self._app_services_

    def get_robots(self):
        return list(self._robots_.values())

    def get_apps(self, robot_name):
        return list(self._apps_[robot_name].values())

    def get_services(self, robot_name, app_name):
        return self._app_services_[robot_name][app_name]

    def list_robots(self):
        return jsonify(self.get_robots())

    def list_apps(self, robot_name):
        return jsonify(self.get_apps(robot_name))

    def list_services(self, robot_name, app_name):
        return jsonify(self.get_services(robot_name, app_name))

    def is_local_register(self, host, port):
        return self._host_ == host and self._port_ == port

    def remote_register(self):
        res = request.get_json(force=True)
        self.register(robot_name=res["robot_name"], app_name=res["app_name"], target_name=res["target_name"], target=res["target"],  target_signature=res["target_signature"], host=res["host"], port=res["port"])
        return res

    def remote_unregister(self):
        res = request.get_json(force=True)
        self.unregister(robot_name=res["robot_name"], app_name=res["app_name"], target_name=res["target_name"], host=res["host"], port=res["port"])
        return res
    
    def register(self, robot_name, app_name, target_name, target, target_signature, host, port):
        target_rule = self.target_rule(robot_name, app_name, target_name)

        if self.is_local_register(host, port) and not robot_name in self._app_services_.keys():
            self._app_services_[robot_name] = {}
            self._apps_[robot_name] = {}        

            robot = {
                        'name': robot_name,
                        'url': self.robot_rule(robot_name=robot_name, host=host, port=port)
                    }

            self._robots_[robot_name] = robot


        app = {
                'name': app_name,
                'url': self.app_rule(robot_name=robot_name, app_name=app_name, host=host, port=port)
              }
          
        self._apps_[robot_name][app_name] = app

        if not app_name in self._app_services_[robot_name].keys():
            self._app_services_[robot_name][app_name] = []

        app = {
                'name': app_name,
                'url': self.app_rule(robot_name=robot_name, app_name=app_name, host=host, port=port)
            }
            
        self._apps_[robot_name][app_name] = app

        service_url = self.target_rule(robot_name=robot_name, app_name=app_name, target_name=target_name, host=host, port=port)

        service = {
                    'name': target_name,
                    'url': service_url,
                    'signature': target_signature
                }

        self._app_services_[robot_name][app_name].append(service)

        self._services_[service_url] = iCubRESTService(name=target_name,
                                                       robot_name=robot_name,
                                                       app_name=app_name,
                                                       url=service_url,
                                                       target=target,
                                                       signature=target_signature)

    def unregister(self, robot_name, app_name, target_name, host, port):
        target_rule = self.target_rule(robot_name=robot_name, app_name=app_name, target_name=target_name, host=host, port=port)
        if app_name in self._apps_[robot_name].keys():
            del self._apps_[robot_name][app_name]
        if app_name in self._app_services_[robot_name].keys():
            del self._app_services_[robot_name][app_name]
        del self._services_[target_rule]


class iCubRESTManager(iCubRESTServer):

    def __init__(self, icubrequestmanager, rule_prefix, host, port, proxy_host, proxy_port):
        iCubRESTServer.__init__(self, rule_prefix, host, port)
        self._proxy_host_ = proxy_host
        self._proxy_port_ = proxy_port
        self._requests_ = {}
        self._request_manager_ = icubrequestmanager
        self._flaskapp_.add_url_rule("/%s/requests" % self._rule_prefix_, methods=['GET'], view_func=self.requests)
        self._flaskapp_.add_url_rule("/%s/<robot_name>/<app_name>/<target_name>/<local_id>" % (self._rule_prefix_), methods=['GET'], view_func=self.single_req_info)
    
    def __del__(self):
        for robot in self.get_robots():
            for app in self.get_apps(robot['name']):
                for service in self.get_services(robot['name'],app['name']):
                    self.unregister_target(robot['name'], app['name'], service['name'], self._host_, self._port_)

    @property
    def request_manager(self):
        return self._request_manager_

    def proxy_rule(self):
        return self.server_rule(self._proxy_host_, self._proxy_port_)

    def amiproxy(self):
        return (self._proxy_host_ == self._host_ and self._proxy_port_ == self._port_)

    def requests(self):
        reqs = []
        if 'id' in request.args:
            return self.req_info(req_id=request.args['id'])
        elif 'target' in request.args:
            return self.target_requests(target=request.args['target'])
        elif 'status' in request.args:
            return self.status_requests(status=request.args['status'])
        elif 'pending' in request.args:
            return self.pending_requests()
        for req_id, req in self._requests_.items():
            reqs.append(req['request'].info())
        return jsonify(reqs)

    def req_info(self, req_id):
        if req_id in self._requests_.keys():
            return jsonify(self._requests_[req_id]['request'].info())
        return jsonify([])

    def single_req_info(self, robot_name, app_name, target_name, local_id):
        req_id = self.target_rule(robot_name, app_name, target_name) + '/' + str(local_id)
        return self.req_info(req_id)

    def target_requests(self, target):
        reqs = []
        for req in self._requests_.values():
            if req['request'].target.__name__ == target:
                reqs.append(req['request'].info())
        return jsonify(reqs)

    def status_requests(self, status):
        reqs = []
        for req in self._requests_.values():
            if req['request'].status == status:
                reqs.append(req['request'].info())
        return jsonify(reqs)

    def pending_requests(self):
        return self.status_requests(status="RUNNING")

    def process_target(self, service):
        res = request.get_json(force=True)
        kwargs =  res
        if 'sync' in request.args:
            wait_for_completed=True
        else:
            wait_for_completed=False

        req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST, target=service.target, name=service.name, prefix=service.url)
        
        self._requests_[req.req_id] = {'robot_name': service.robot_name,
                                       'app_name': service.app_name,
                                       'request': req}
        self.request_manager.run_request(req, wait_for_completed, **kwargs)
        if wait_for_completed:
            return jsonify(req.retval)
        return jsonify(req.req_id)

    def register_target(self, robot_name, app_name, target_name, target, target_signature):
        self.register(robot_name, app_name, target_name, target, target_signature, self._host_, self._port_)

        if not self.amiproxy():

            data = {
                        "robot_name": robot_name,
                        "app_name": app_name,
                        "target_name": target_name,
                        "target": None,
                        "target_signature": target_signature,
                        "host": self._host_,
                        "port": self._port_ 
                    }

            res = requests.post('http://%s:%s/%s/register' % (self._proxy_host_, self._proxy_port_, self._rule_prefix_), json=data)
            return res.content
        return True

    def unregister_target(self, robot_name, app_name, target_name, host, port):
        self.unregister(robot_name, app_name, target_name, host, port)
        if not self.amiproxy():

            data = {
                        "robot_name": robot_name,
                        "app_name": app_name,
                        "target_name": target_name,
                        "host": host,
                        "port": port
                    }
        
            res = requests.post('http://%s:%s/%s/unregister' % (self._proxy_host_, self._proxy_port_, self._rule_prefix_), json=data)
            return res.content



class PyiCubRESTfulClient:

    def __init__(self, host, port, rule_prefix='pyicub'):
        self._host_ = host
        self._port_ = port
        self._rule_prefix_ = rule_prefix
        self._header_ = "http://%s:%d/%s/" % (self._host_, self._port_, self._rule_prefix_)

    def __run__(self, robot_name, app_name, target_name, sync, *args, **kwargs):
        data = kwargs
        url = self._header_ + robot_name + '/' + app_name + '/' + target_name
        if sync:
            url += '?sync'
        res = requests.post(url=url, json=data)
        return res.json()

    def run_target(self, robot_name, app_name, target_name, *args, **kwargs):
        return self.__run__(robot_name, app_name, target_name, True, *args, **kwargs)

    def run_target_async(self, robot_name, app_name, target_name, *args, **kwargs):
        return self.__run__(robot_name, app_name, target_name, False, *args, **kwargs)
    
    def get_request_info(self, req_id):
        return requests.get(url=req_id, json={}).json()

    def is_request_running(self, req_id):
        req = self.get_request_info(req_id)
        return req['status'] == iCubRequest.RUNNING

    def wait_until_completed(self, req_id):
        while True:
            req = self.get_request_info(req_id)
            if req['status'] != iCubRequest.RUNNING:
                return req['retval']
            time.sleep(0.01)

class PyiCubApp(metaclass=SingletonMeta):

    def __init__(self, logging=False, logging_path=None, restmanager_proxy_host=None, restmanager_proxy_port=None):

        PYICUB_LOGGING = os.getenv('PYICUB_LOGGING')
        PYICUB_LOGGING_PATH = os.getenv('PYICUB_LOGGING_PATH')
        PYICUB_API = os.getenv('PYICUB_API')
        PYICUB_API_RESTMANAGER_HOST = os.getenv('PYICUB_API_RESTMANAGER_HOST')
        PYICUB_API_RESTMANAGER_PORT = os.getenv('PYICUB_API_RESTMANAGER_PORT')
        PYICUB_API_PROXY_HOST = os.getenv('PYICUB_API_PROXY_HOST')
        PYICUB_API_PROXY_PORT = os.getenv('PYICUB_API_PROXY_PORT')

        if PYICUB_LOGGING:
            if PYICUB_LOGGING == 'true':
                logging = True

        self._request_manager_ = None
        self._rest_manager_ = None
        self._logging_ = logging
        self._logger_ = YarpLogger.getLogger() #PyicubLogger.getLogger() 

        if self._logging_:
            self._logger_.enable_logs()
            self._logger_ = YarpLogger.getLogger() #PyicubLogger.getLogger()

            if PYICUB_LOGGING_PATH:
                logging_path = PYICUB_LOGGING_PATH

                if os.path.isdir(logging_path):
                    if isinstance(self._logger_, PyicubLogger):
                        self._logger_.configure(PyicubLogger.LOGGING_LEVEL, PyicubLogger.FORMAT, True, logging_path)
            else:
                if isinstance(self._logger_, PyicubLogger):
                    self._logger_.configure(PyicubLogger.LOGGING_LEVEL, PyicubLogger.FORMAT)
        else:
            self._logger_.disable_logs()

        self._request_manager_ = iCubRequestsManager(self._logger_, self._logging_, logging_path)

        if not PYICUB_API:
            PYICUB_API = False
        elif PYICUB_API == 'true':
            if not (PYICUB_API_RESTMANAGER_HOST and PYICUB_API_RESTMANAGER_PORT):
                PYICUB_API_RESTMANAGER_HOST = "0.0.0.0"
                PYICUB_API_RESTMANAGER_PORT = 9001
            if PYICUB_API_PROXY_HOST and PYICUB_API_PROXY_PORT:
                restmanager_proxy_host = PYICUB_API_PROXY_HOST
                restmanager_proxy_port = int(PYICUB_API_PROXY_PORT)
            else:
                restmanager_proxy_host = "0.0.0.0"
                restmanager_proxy_port = 9001
            PYICUB_API_RESTMANAGER_PORT = firstAvailablePort(PYICUB_API_RESTMANAGER_HOST, int(PYICUB_API_RESTMANAGER_PORT))            
            self._rest_manager_ = iCubRESTManager(icubrequestmanager=self._request_manager_, rule_prefix="pyicub",  host=PYICUB_API_RESTMANAGER_HOST, port=PYICUB_API_RESTMANAGER_PORT, proxy_host=restmanager_proxy_host, proxy_port=restmanager_proxy_port)
        
    @property
    def logger(self):
        return self._logger_

    @property
    def request_manager(self):
        return self._request_manager_

    @property
    def rest_manager(self):
        return self._rest_manager_


class iCubRESTApp:

    def __init__(self, robot_name="icub", **kargs):
        self._name_ = self.__class__.__name__
        self.__app__ = PyiCubApp()

        SIMULATION = os.getenv('ICUB_SIMULATION')
        if SIMULATION:
            if SIMULATION == 'true':
                robot_name = "icubSim"

        self.__robot_name__ = robot_name

        if self.__is_icub_managed__():
            self.__icub__ = None
        else:
            self.__icub__ = iCub(robot_name=robot_name, request_manager=self.__app__.request_manager)
            if self.__icub__.exists():
                self.__register_icub_helper__()
        self.__register_class__(robot_name=self.__robot_name__, app_name=self._name_, cls=self)
        self.__args_template__ = kargs
        self.__args__ = {}
        self.__actions__ = {}
        self.__configure_default_args__()

    def __is_icub_managed__(self):
        url = self.rest_manager.proxy_rule() + '/' + self.__robot_name__ + '/helper'
        try:
            res = requests.get(url, json={})
            return res.status_code == 200
        except:
            return False
        
    def __register_icub_helper__(self):
        app_name = "helper"
        self.__register_method__(robot_name=self.__robot_name__, app_name=app_name, method=self.icub.playAction)
        self.__register_method__(robot_name=self.__robot_name__, app_name=app_name, method=self.icub.importActionFromJSONDict)
        self.__register_method__(robot_name=self.__robot_name__, app_name=app_name, method=self.icub.importActionFromTemplateJSONDict)
        if self.icub.gaze:
            self.__register_class__(robot_name=self.__robot_name__, app_name=app_name, cls=self.icub.gaze, class_name='gaze')
        if self.icub.speech:
            self.__register_class__(robot_name=self.__robot_name__, app_name=app_name, cls=self.icub.speech, class_name='speech')
        if self.icub.emo:
            self.__register_class__(robot_name=self.__robot_name__, app_name=app_name, cls=self.icub.emo, class_name='emo')

    def __register_class__(self, robot_name, app_name, cls, class_name: str=''):
        target_prefix = class_name
        for method in getPublicMethods(cls):
            if class_name:
                target_prefix = class_name + '.'
            self.__app__.rest_manager.register_target(robot_name=robot_name, app_name=app_name, target_name=target_prefix+getattr(cls, method).__name__, target=getattr(cls, method), target_signature=str(inspect.signature(getattr(cls, method))) )

    def __register_method__(self, robot_name, app_name, method):
        self.__app__.rest_manager.register_target(robot_name=robot_name, app_name=app_name, target_name=method.__name__, target=method, target_signature=str(inspect.signature(method)) )
    
    def __configure_default_args__(self):
        for k,v in self.__args_template__.items():
            if type(v) is list:
                val = v[0]
            else:
                val = v
            self.__args__[k] = val
    
    def importActions(self, path):
        json_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
        for f in json_files:
            if self.icub:
                action_id = self.icub.importActionFromJSONFile(os.path.join(path, f))
            else:
                url = self.rest_manager.proxy_rule() + '/' + self.__robot_name__ + '/helper/importActionFromJSONDict'
                data = {}
                data["JSON_dict"] = importFromJSONFile(os.path.join(path, f))
                res = requests.post(url=url, json=data)
                res = requests.get(res.json())
                action_id = res.json()['retval']
            self.__actions__[os.path.join(os.path.basename(path),f)] = action_id

    def importActionFromTemplate(self, template_file, params_files):
        if self.icub:
            action_id = self.icub.importActionFromTemplateJSONFile(JSON_file=template_file, params_files=params_files)
        else:
            url = self.rest_manager.proxy_rule() + '/' + self.__robot_name__ + '/helper/importActionFromTemplateJSONDict'
            data = {}
            data["JSON_dict"] = importFromJSONFile(template_file)
            data["params_dict"] = {}
            for param in params_files:
                param_dict = importFromJSONFile(param)
                data["params_dict"].update(param_dict)
            res = requests.post(url=url, json=data)
            res = requests.get(res.json())
            action_id = res.json()['retval']
        key = ""
        key += os.path.basename(template_file)
        for param in params_files:
            key = key + ',' + os.path.basename(param)
        self.__actions__[key] = action_id

    def getArgsTemplate(self):
        return self.__args_template__

    def getArgs(self):
        return self.__args__

    def getActions(self):
        return self.__actions__

    def setArgs(self, input_args: dict):
        for k,v in input_args.items():
            self.__args__[k] = v
        return True

    def getArg(self, name: str):
        return self.__args__[name]

    def setArg(self, name: str, value: object):
        self.__args__[name] = value
        return True

    @property
    def icub(self):
        return self.__icub__

    @property
    def app_name(self):
        return self._name_

    @property
    def rest_manager(self):
        return self.__app__.rest_manager
