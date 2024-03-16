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

try:
    import yarp
    from pyicub.helper import iCub
except ImportError:
    print("The 'yarp' module is not installed. Some functionality may be limited.")

from pyicub.requests import iCubRequest
from pyicub.utils import SingletonMeta, getPyiCubInfo, getPublicMethods, getDecoratedMethods, firstAvailablePort, importFromJSONFile, exportJSONFile
from pyicub.core.logger import PyicubLogger, YarpLogger
from pyicub.requests import iCubRequestsManager, iCubRequest
from pyicub.fsm import FSM
from pyicub.actions import iCubFullbodyAction
from flask import Flask, jsonify, request
from flask_cors import CORS
from urllib.parse import urlparse, urlsplit

import requests
import json
import time
import os
import inspect
import threading
import functools
import importlib

class RESTJSON:

    def __init__(self, json_dict=None):
        if json_dict:
            self.fromJSON(json_dict)

    def fromJSON(self, json_dict: dict):
        for k,v in json_dict.items():
            self.__dict__[k] = v

    def toJSON(self):
        return vars(self)


class RESTRobot(RESTJSON):

    def __init__(self, name=None, url=None, json_dict=None):
        self.name = name
        self.url = url
        RESTJSON.__init__(self, json_dict)
    
        
class RESTApp(RESTJSON):

    def __init__(self, name=None, url=None, json_dict=None):
        self.name = name
        self.url = url
        RESTJSON.__init__(self, json_dict)


class RESTTopic(RESTJSON):

    def __init__(self, name=None, robot_name=None, app_name=None, subscriber_rule=None, json_dict=None):
        self.name = name
        self.robot_name = robot_name
        self.app_name = app_name
        self.subscriber_rule = subscriber_rule
        RESTJSON.__init__(self, json_dict)

class iCubRESTService(RESTJSON):

    def __init__(self, name=None, robot_name=None, app_name=None, url=None, target=None, signature=None, json_dict=None):
        self.name = name
        self.robot_name = robot_name
        self.app_name = app_name
        self.url = url
        self.target = target
        self.signature = signature


class RESTService(RESTJSON):

    def __init__(self, service: iCubRESTService=None, json_dict=None):
        if service:
            self.name = service.name
            self.robot_name = service.robot_name
            self.app_name = service.app_name
            self.url = service.url
            self.target = str(service.target)
            self.signature = service.signature
        RESTJSON.__init__(self, json_dict)


class iCubRESTServer(metaclass=SingletonMeta):

    def __init__(self, rule_prefix, host, port):
        self._services_ = {}
        self._app_services_ = {}
        self._apps_ = {}
        self._robots_ = []
        self._flaskapp_ = Flask(__name__)
        CORS(self._flaskapp_)
        self._host_ = host
        self._port_ = port
        self._rule_prefix_ = rule_prefix
        self._on_enter_callbacks_ = {}
        self._on_exit_callbacks_ = {}
        self._flaskapp_.add_url_rule("/", methods=['GET'], view_func=self.info)
        self._flaskapp_.add_url_rule("/%s" % self._rule_prefix_, methods=['GET'], view_func=self.get_robots)
        self._flaskapp_.add_url_rule("/%s/tree" % self._rule_prefix_, methods=['GET'], view_func=self.get_tree)
        self._flaskapp_.add_url_rule("/%s/register" % self._rule_prefix_, methods=['POST'], view_func=self.remote_register)
        self._flaskapp_.add_url_rule("/%s/unregister" % self._rule_prefix_, methods=['POST'], view_func=self.remote_unregister)
        self._flaskapp_.add_url_rule("/%s/notify" % self._rule_prefix_, methods=['POST'], view_func=self.remote_notify)
        self._flaskapp_.add_url_rule("/%s/subscribe" % self._rule_prefix_, methods=['POST'], view_func=self.remote_subscribe)
        self._flaskapp_.add_url_rule("/%s/unsubscribe" % self._rule_prefix_, methods=['POST'], view_func=self.remote_unsubscribe)
        self._flaskapp_.add_url_rule("/%s/subscribers" % self._rule_prefix_, methods=['GET'], view_func=self.subscribers)

        self._flaskapp_.add_url_rule("/%s/<robot_name>" % self._rule_prefix_, methods=['GET'], view_func=self.get_apps)
        self._flaskapp_.add_url_rule("/%s/<robot_name>/<app_name>" % self._rule_prefix_, methods=['GET'], view_func=self.get_services)
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
                self._flaskapp_.run(self._host_, self._port_, threaded=True)
                stop = True
            except:
                self._port_ += 1
        for topic_uri in self._on_enter_callbacks_.keys():
            self.unsubscribe(topic_uri)

     
    def shutdown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def wrapper_target(self, robot_name, app_name, target_name):
        target_rule = self.target_rule(robot_name, app_name, target_name)
        if request.method == 'GET':
            return self._app_services_[robot_name][app_name][target_name]
        elif request.method == 'POST':
            if not type(self._services_[target_rule].target) is str:
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
        return self._robots_

    def get_apps(self, robot_name):
        return list(self._apps_[robot_name].values())

    def get_services(self, robot_name, app_name):
        return self._app_services_[robot_name][app_name]
    
    def is_local_register(self, host, port):
        return self._host_ == host and self._port_ == port

    def remote_register(self):
        res = request.get_json(force=True)
        service = RESTService(json_dict=res)
        self.register(robot_name=service.robot_name, app_name=service.app_name, target_name=service.name, target=service.target,  target_signature=service.signature, url=service.url)
        return res

    def remote_unregister(self):
        res = request.get_json(force=True)
        service = RESTService(json_dict=res)
        self.unregister(robot_name=service.robot_name, app_name=service.app_name, target_name=service.name, url=service.url)
        return res

    def register(self, robot_name, app_name, target_name, target, target_signature, url):
        host = urlparse(url).hostname
        port = urlparse(url).port

        if self.is_local_register(host, port) and not robot_name in self._app_services_.keys():
            self._app_services_[robot_name] = {}
            self._apps_[robot_name] = {}

            robot = RESTRobot(name=robot_name, url=self.robot_rule(robot_name=robot_name, host=host, port=port))
            self._robots_.append(robot.toJSON())

        app = RESTApp(name=app_name, url=self.app_rule(robot_name=robot_name, app_name=app_name, host=host, port=port))
          
        if not app_name in self._app_services_[robot_name].keys():
            self._app_services_[robot_name][app_name] = {}
            
        self._apps_[robot_name][app_name] = app.toJSON()

        service = iCubRESTService(name=target_name,
                                robot_name=robot_name,
                                app_name=app_name,
                                url=url,
                                target=target,
                                signature=target_signature)
        
        self._services_[url] = service
        rs = RESTService(service=service)
        self._app_services_[robot_name][app_name][target_name] = rs.toJSON()

    def unregister(self, robot_name, app_name, target_name, url):
        if app_name in self._apps_[robot_name].keys():
            del self._apps_[robot_name][app_name]
        if app_name in self._app_services_[robot_name].keys():
            del self._app_services_[robot_name][app_name]
        del self._services_[url]

    def remote_subscribe(self):
        res = request.get_json(force=True)
        topic = RESTTopic(json_dict=res)
        self.subscribe_topic(robot_name=topic.robot_name, app_name=topic.app_name, target_name=topic.name, subscriber_rule=topic.subscriber_rule)
        return res

    def remote_unsubscribe(self):
        res = request.get_json(force=True)
        topic = RESTTopic(json_dict=res)
        self.unsubscribe_topic(robot_name=topic.robot_name, app_name=topic.app_name, target_name=topic.name, subscriber_rule=topic.subscriber_rule)
        return res

    def remote_notify(self):
        res = request.get_json(force=True)
        thread = None
        if res["topic_uri"] in self._on_enter_callbacks_.keys() and res["event"] == "enter":
            thread = threading.Thread(target=self._on_enter_callbacks_[res["topic_uri"]], args=(res,))
            thread.start()
        if res["topic_uri"] in self._on_exit_callbacks_.keys() and res["event"] == "exit":
            thread = threading.Thread(target=self._on_exit_callbacks_[res["topic_uri"]], args=(res,))
            thread.start()
        thread.join()
        return res

    def subscribe(self, topic_uri, on_enter, on_exit):
        split_url = urlsplit(topic_uri)
        publisher_rule = f"{split_url.scheme}://{split_url.netloc}{split_url.path.split('/')[0]}/{split_url.path.split('/')[1]}"
        robot_name = split_url.path.split('/')[2]
        app_name = split_url.path.split('/')[3]
        target_name = split_url.path.split('/')[4]
        topic = RESTTopic(name=target_name, robot_name=robot_name, app_name=app_name, subscriber_rule=self.server_rule())
        self._on_enter_callbacks_[topic_uri] = on_enter
        self._on_exit_callbacks_[topic_uri] = on_exit
        res = requests.post('%s/subscribe' % publisher_rule, json=topic.toJSON())
        return res.content

    def unsubscribe(self, topic_uri):
        split_url = urlsplit(topic_uri)
        publisher_rule = f"{split_url.scheme}://{split_url.netloc}{split_url.path.split('/')[0]}/{split_url.path.split('/')[1]}"
        robot_name = split_url.path.split('/')[2]
        app_name = split_url.path.split('/')[3]
        target_name = split_url.path.split('/')[4]
        topic = RESTTopic(name=target_name, robot_name=robot_name, app_name=app_name, subscriber_rule=self.server_rule())
        res = requests.post('%s/unsubscribe' % publisher_rule, json=topic.toJSON())
        return res.content

class iCubRESTManager(iCubRESTServer):

    def __init__(self, icubrequestmanager, rule_prefix, host, port, proxy_host, proxy_port):
        iCubRESTServer.__init__(self, rule_prefix, host, port)
        self._proxy_host_ = proxy_host
        self._proxy_port_ = proxy_port
        self._requests_ = {}
        self._subscribers_ = {}
        self._request_manager_ = icubrequestmanager
        self._flaskapp_.add_url_rule("/%s/requests" % self._rule_prefix_, methods=['GET'], view_func=self.requests)
        self._flaskapp_.add_url_rule("/%s/<robot_name>/<app_name>/<target_name>/<local_id>" % (self._rule_prefix_), methods=['GET'], view_func=self.single_req_info)
    
    def __del__(self):
        for robot in self.get_robots():
            for app in self.get_apps(robot['name']):
                for service in self.get_services(robot['name'],app['name']).values():
                    self.unregister_target(robot['name'], app['name'], service['name'], self._host_, self._port_)

    @property
    def request_manager(self):
        return self._request_manager_

    @property
    def proxy_host(self):
        return self._proxy_host_

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

    def subscribe_topic(self, robot_name, app_name, target_name, subscriber_rule):
        target_rule = self.target_rule(robot_name, app_name, target_name)
        if not target_rule in self._subscribers_.keys():
            self._subscribers_[target_rule] = []
        self._subscribers_[target_rule].append(subscriber_rule)

    def unsubscribe_topic(self, robot_name, app_name, target_name, subscriber_rule):
        target_rule = self.target_rule(robot_name, app_name, target_name)
        if target_rule in self._subscribers_.keys():
            if subscriber_rule in self._subscribers_[target_rule]:
                self._subscribers_[target_rule].remove(subscriber_rule)
                if len(self._subscribers_[target_rule]) == 0:
                    del self._subscribers_[target_rule]

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

    def subscribers(self):
        return self._subscribers_

    def pending_requests(self):
        return self.status_requests(status="RUNNING")

    def process_target(self, service):
        res = request.get_json(force=True)
        kwargs =  res
        wait_for_completed=False
        req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST, target=service.target, name=service.name, prefix=service.url)
        
        self._requests_[req.req_id] = {'robot_name': service.robot_name,
                                       'app_name': service.app_name,
                                       'request': req}
        self.request_manager.run_request(req, wait_for_completed, **kwargs)
        if 'sync' in request.args:
            wait_for_completed=True
        else:
            wait_for_completed=False
        target_rule = self.target_rule(service.robot_name, service.app_name, service.name)
        if target_rule in self._subscribers_.keys():
            for subscriber in self._subscribers_[target_rule]:
                thread = threading.Thread(target=self.notify_subscriber, args=(subscriber, target_rule, req, res,))
                thread.start()

        if wait_for_completed:
            req.wait_for_completed()
            return jsonify(req.retval)
        return jsonify(req.req_id)

    def notify_subscriber(self, subscriber_url, target_rule, req, input_json):
        res = {}
        res["req_info"] = req.info()
        res["input_json"] = input_json
        res["topic_uri"] = target_rule
        try:
            res["event"] = "enter"
            response = requests.post("%s/notify" % subscriber_url, json=res)
            req.wait_for_completed()
            res["event"] = "exit"
            res["req_info"] = req.info()
            response = requests.post("%s/notify" % subscriber_url, json=res)
        except Exception as e:
            print(e)
        return response.status_code

    def register_target(self, robot_name, app_name, target_name, target, target_signature):
        url = self.target_rule(robot_name=robot_name, app_name=app_name, target_name=target_name, host=self._host_, port=self._port_)
        self.register(robot_name, app_name, target_name, target, target_signature, url)

        if not self.amiproxy():
            service = iCubRESTService(name=target_name,
                                        robot_name=robot_name,
                                        app_name=app_name,
                                        url=url,
                                        target=target,
                                        signature=target_signature)

            rs = RESTService(service=service)

            res = requests.post('%s/register' % self.proxy_rule(), json=rs.toJSON())
            return res.content
        return True

    def unregister_target(self, robot_name, app_name, target_name, host, port):
        url = self.target_rule(robot_name=robot_name, app_name=app_name, target_name=target_name, host=host, port=port)
        self.unregister(robot_name, app_name, target_name, url)
        if not self.amiproxy():
            service = iCubRESTService(name=target_name,
                                    robot_name=robot_name,
                                    app_name=app_name,
                                    url=url,
                                    target=None,
                                    signature=None)
            rs = RESTService(service=service)
            res = requests.post('%s/unregister' % self.proxy_rule(), json=rs.toJSON())
            return res.content

class PyiCubApp(metaclass=SingletonMeta):

    def __init__(self, logging=False, logging_path=None, restmanager_proxy_host=None, restmanager_proxy_port=None):

        PYICUB_LOGGING = os.getenv('PYICUB_LOGGING')
        PYICUB_LOGGING_PATH = os.getenv('PYICUB_LOGGING_PATH')
        PYICUB_API = os.getenv('PYICUB_API')
        PYICUB_API_RESTMANAGER_HOST = os.getenv('PYICUB_API_RESTMANAGER_HOST')
        PYICUB_API_RESTMANAGER_PORT = os.getenv('PYICUB_API_RESTMANAGER_PORT')
        PYICUB_API_PROXY_HOST = os.getenv('PYICUB_API_PROXY_HOST')
        PYICUB_API_PROXY_PORT = os.getenv('PYICUB_API_PROXY_PORT')
        PYICUB_API_PROXY_SCHEME = os.getenv('PYICUB_API_PROXY_SCHEME')

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


def rest_service(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    setattr(wrapper, '__decorators__', ['rest_service'])
    return wrapper

class PyiCubRESTfulServer(PyiCubApp):

    custom_rest_services = {}

    def __init__(self, robot_name='generic', **kargs):
        PyiCubApp.__init__(self)
        self._name_ = self.__class__.__name__
        self.__robot_name__ = robot_name
        self.__fsm__ = None
        self.__register_utils__(app_name=self._name_)
        self.__register_custom_methods__(robot_name=robot_name, app_name=self.name, cls=self, class_name=self.name)
        self.__args_template__ = kargs
        self.__args__ = {}
        self.__configure_default_args__()

    def __register_utils__(self, app_name):
        self.__register_method__(robot_name=self.robot_name, app_name=app_name, method=self.__configure__, target_name='utils.configure')
        self.__register_method__(robot_name=self.robot_name, app_name=app_name, method=self.getServices, target_name='utils.getServices')
        self.__register_method__(robot_name=self.robot_name, app_name=app_name, method=self.getArgsTemplate, target_name='utils.getArgsTemplate')
        self.__register_method__(robot_name=self.robot_name, app_name=app_name, method=self.getArgs, target_name='utils.getArgs')
        self.__register_method__(robot_name=self.robot_name, app_name=app_name, method=self.setArgs, target_name='utils.setArgs')
        self.__register_method__(robot_name=self.robot_name, app_name=app_name, method=self.getArg, target_name='utils.getArg')
        self.__register_method__(robot_name=self.robot_name, app_name=app_name, method=self.setArg, target_name='utils.setArg')

    def configure(self, input_args):
        return {}

    @property
    def name(self):
        return self._name_

    @property
    def robot_name(self):
        return self.__robot_name__

    @property
    def fsm(self):
        return self.__fsm__

    def __configure_default_args__(self):
        for k,v in self.__args_template__.items():
            if type(v) is list:
                val = v[0]
            else:
                val = v
            self.__args__[k] = val

    def __register_method__(self, robot_name, app_name, method, target_name: str=''):
        if not target_name:
            target_name = method.__name__
        signature = inspect.signature(method)
        args_dict = {param.name: param.default for param in signature.parameters.values() if param.default is not param.empty}
        args_dict.update({param.name: '' for param in signature.parameters.values() if param.default is param.empty or param.default is None})
        self.rest_manager.register_target(robot_name=robot_name, app_name=app_name, target_name=target_name, target=method, target_signature=args_dict)

    def __register_class__(self, robot_name, app_name, cls, class_name: str=''):
        target_prefix = class_name
        for method in getPublicMethods(cls):
            if class_name:
                target_prefix = class_name + '.'
            if "__name__" in getattr(cls, method).__dict__.keys():
                target_name = getattr(cls, method).__name__
            else:
                target_name = str(method)
            signature = inspect.signature(getattr(cls, method))
            args_dict = {param.name: param.default for param in signature.parameters.values() if param.default is not param.empty}
            args_dict.update({param.name: '' for param in signature.parameters.values() if param.default is param.empty or param.default is None})
            self.rest_manager.register_target(robot_name=robot_name, app_name=app_name, target_name=target_prefix+target_name, target=getattr(cls, method), target_signature=args_dict)

    def __register_custom_methods__(self, robot_name, app_name, cls, class_name: str=''):
        target_prefix = class_name
        for method in getDecoratedMethods(cls, "rest_service"):
            if class_name:
                target_prefix = class_name + '.'
            if "__name__" in getattr(cls, method).__dict__.keys():
                target_name = getattr(cls, method).__name__
            else:
                target_name = str(method)
            signature = inspect.signature(getattr(cls, method))
            args_dict = {param.name: param.default for param in signature.parameters.values() if param.default is not param.empty}
            args_dict.update({param.name: '' for param in signature.parameters.values() if param.default is param.empty or param.default is None})
            self.rest_manager.register_target(robot_name=robot_name, app_name=app_name, target_name=target_prefix+target_name, target=getattr(cls, method), target_signature=args_dict)

    def __configure__(self, input_args: dict):
        self.setArgs(input_args)
        self.configure(input_args)
        return True
    
    def getServices(self):
        return list(self.rest_manager.get_services(self.robot_name, self.name).keys())

    def getArgsTemplate(self):
        return self.__args_template__

    def initHelper(self):
        return {}

    def getArgs(self):
        return self.__args__

    def setArgs(self, input_args: dict):
        for k,v in input_args.items():
            self.__args__[k] = v
        return

    def getArg(self, name: str):
        return self.__args__[name]

    def setArg(self, name: str, value: object):
        self.__args__[name] = value
        return True
    
    def setFSM(self, fsm: FSM, session_id=0):
        self.__fsm__ = fsm
        if isinstance(fsm, iCubFSM):
            fsm.setApp(self)
        fsm.setSessionID(session_id)
        self.__register_class__(robot_name=self.__robot_name__, app_name=self._name_, cls=self.__fsm__, class_name='fsm')


class iCubRESTApp(PyiCubRESTfulServer):

    def __init__(self, robot_name="icub", action_repository_path='', **kargs):
        self.__icub__ = None

        SIMULATION = os.getenv('ICUB_SIMULATION')
        if SIMULATION:
            if SIMULATION == 'true':
                robot_name = "icubSim"

        PyiCubRESTfulServer.__init__(self, robot_name=robot_name, **kargs)
        
        self.__action_repository__ = action_repository_path

        if self.__is_icub_managed__():
            self.__icub__ = None
        else:
            self.__icub__ = iCub(robot_name=robot_name, request_manager=self.request_manager, proxy_host=self.rest_manager.proxy_host)
            if self.__icub__.exists():
                self.__register_icub_helper__()
        
        if action_repository_path:
            self.importActions(path=action_repository_path)

        self.__configure__(input_args=self.__args__)
    
    def __configure__(self, input_args: dict):
        self.setArgs(input_args)
        self.configure(input_args)
        if self.fsm:
            for action in self.fsm.actions.values():
                self.importAction(action, name_prefix=self.name + '.' + self.fsm.name)
        return True

    def configure(self, input_args):
        return {}

    def __is_icub_managed__(self):
        url = self.rest_manager.proxy_rule() + '/' + self.__robot_name__ + '/helper/info'
        try:
            res = requests.get(url, json={})
            return res.status_code == 200
        except:
            return False

    def info(self):
        return self.icub
        
    def __register_icub_helper__(self):
        app_name = "helper"
        self.__register_method__(robot_name=self.robot_name, app_name=app_name, method=self.initHelper, target_name='utils.getArgsTemplate')
        self.__register_method__(robot_name=self.robot_name, app_name=app_name, method=self.initHelper, target_name='utils.configure')
        self.__register_method__(robot_name=self.__robot_name__, app_name=app_name, method=self.info, target_name='info')
        if self.icub.actions_manager:
            self.__register_method__(robot_name=self.__robot_name__, app_name=app_name, method=self.playAction, target_name='actions.playAction')
            self.__register_method__(robot_name=self.__robot_name__, app_name=app_name, method=self.getActions, target_name='actions.getActions')
            self.__register_method__(robot_name=self.__robot_name__, app_name=app_name, method=self.importActionFromJSONDict, target_name='actions.importAction')
        if self.icub.gaze:
            self.__register_class__(robot_name=self.__robot_name__, app_name=app_name, cls=self.icub.gaze, class_name='gaze')
        if self.icub.speech:
            self.__register_class__(robot_name=self.__robot_name__, app_name=app_name, cls=self.icub.speech, class_name='speech')
        if self.icub.emo:
            self.__register_class__(robot_name=self.__robot_name__, app_name=app_name, cls=self.icub.emo, class_name='emo')
        if self.icub.cam_right:
            self.__register_class__(robot_name=self.__robot_name__, app_name=app_name, cls=self.icub.cam_right, class_name='cam_right')
        if self.icub.cam_left:
            self.__register_class__(robot_name=self.__robot_name__, app_name=app_name, cls=self.icub.cam_left, class_name='cam_left')

    def importActionFromJSONFile(self, JSON_file):
        JSON_dict = importFromJSONFile(JSON_file)
        return self.importActionFromJSONDict(JSON_dict=JSON_dict)
  
    def importActions(self, path):
        json_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
        for f in json_files:
            self.importActionFromJSONFile(os.path.join(path, f))

    def importActionFromJSONDict(self, JSON_dict, name_prefix=None):
        if not name_prefix:
            name_prefix = self.__class__.__name__
        if self.icub:
            action_id = self.icub.importActionFromJSONDict(JSON_dict, name_prefix=name_prefix)
        else:
            data = {}
            data['JSON_dict'] = JSON_dict
            data['name_prefix'] = name_prefix
            url = self.rest_manager.proxy_rule() + '/' + self.__robot_name__ + '/helper/actions.importAction'
            res = requests.post(url=url, json=data)
            res = requests.get(res.json())
            action_id = res.json()['retval']
        return action_id

    def playAction(self, action_id: str, wait_for_completed=True):
        if self.icub:
            req = self.icub.playAction(action_id=action_id, wait_for_completed=wait_for_completed)
            return 
        else:
            data = {}
            data['action_id'] = action_id
            if(wait_for_completed):
                url = self.rest_manager.proxy_rule() + '/' + self.__robot_name__ + '/helper/actions.playAction?sync'
                res = requests.post(url=url, json=data)
                return res.req_id
            else:
                url = self.rest_manager.proxy_rule() + '/' + self.__robot_name__ + '/helper/actions.playAction'
                res = requests.post(url=url, json=data)
                res = requests.get(res.json())
                return res
    
    def getActions(self):
        return list(self.icub.getActions())

    def importAction(self, action: iCubFullbodyAction, name_prefix=None):
        if not name_prefix:
            name_prefix = self.__class__.__name__        
        json_string = json.dumps(action, default=lambda x: x.toJSON(), indent=2)
        json_dict = json.loads(json_string)
        return self.importActionFromJSONDict(JSON_dict=json_dict, name_prefix=name_prefix)

    @property
    def icub(self):
        return self.__icub__


class iCubRESTSubscriber(PyiCubApp):

    def subscribe_topic(self, topic_uri, on_enter=None, on_exit=None):
        self.rest_manager.subscribe(topic_uri=topic_uri, on_enter=on_enter, on_exit=on_exit)

    def run_forever(self):
        self.rest_manager.run_forever()

class RESTSubscriberFSM(iCubRESTSubscriber):

    def __init__(self, server_host, server_port, robot_name, app_name):
        iCubRESTSubscriber.__init__(self)
        self.__server_host__ = server_host
        self.__server_port__ = server_port
        self.__robot_name__ = robot_name
        self.__app_name__ = app_name
        self.__triggers__ = {}
        self.__root_state__ = None
        self.__leaf_states__ = []
        self.__subscribe__()


    def __on_enter_state__(self, args):
        trigger = args["input_json"]["trigger"]
        state = self.__triggers__[trigger]
        target = self.rest_manager.target_rule(self.__robot_name__, self.__app_name__, "fsm.toJSON?sync", host=self.__server_host__, port=self.__server_port__)
        res = requests.post(target, json={})
        session_id = res.json()['session_id']
        session_count = res.json()['session_count']
        fsm_name = res.json()['name']
        if not state == FSM.INIT_STATE:
            if state == self.__root_state__:                
                self.on_enter_fsm(fsm_name=fsm_name, session_id=session_id, session_count=session_count)
            self.on_enter_state(fsm_name=fsm_name, session_id=session_id, session_count=session_count, state_name=state)

    def __on_exit_state__(self, args):
        trigger = args["input_json"]["trigger"]
        state = self.__triggers__[trigger]
        target = self.rest_manager.target_rule(self.__robot_name__, self.__app_name__, "fsm.toJSON?sync", host=self.__server_host__, port=self.__server_port__)
        res = requests.post(target, json={})
        session_id = res.json()['session_id']
        session_count = res.json()['session_count']
        fsm_name = res.json()['name']
        if not state == FSM.INIT_STATE:
            self.on_exit_state(fsm_name=fsm_name, session_id=session_id, session_count=session_count, state_name=state)
            if state in self.__leaf_states__:
                self.on_exit_fsm(fsm_name=fsm_name, session_id=session_id, session_count=session_count)

    def __subscribe__(self):
        topic_uri = self.rest_manager.target_rule(self.__robot_name__, self.__app_name__, "fsm.runStep", host=self.__server_host__, port=self.__server_port__)
        self.subscribe_topic(topic_uri=topic_uri, on_enter=self.__on_enter_state__, on_exit=self.__on_exit_state__)
        target = self.rest_manager.target_rule(self.__robot_name__, self.__app_name__, "fsm.toJSON?sync", host=self.__server_host__, port=self.__server_port__)
        res = requests.post(target, json={})
        transitions = list(res.json()['transitions'])
        self.__leaf_states__ = []
        for transition in transitions:
            if transition['source'] == FSM.INIT_STATE:
                self.__root_state__ = transition['dest']
            if transition['dest'] == FSM.INIT_STATE:
                self.__leaf_states__.append(transition['source'])
            self.__triggers__[transition['trigger']] = transition['dest']

    def on_enter_state(self, fsm_name, session_id, session_count, state_name):
        raise Exception("Method iCubRESTSubscriberFSM.on_enter_state is not implemented!")

    def on_exit_state(self, fsm_name, session_id, session_count, state_name):
        raise Exception("Method iCubRESTSubscriberFSM.on_exit_state is not implemented!")

    def on_enter_fsm(self, fsm_name, session_id, session_count):
        raise Exception("Method iCubRESTSubscriberFSM.on_enter_fsm is not implemented!")

    def on_exit_fsm(self, fsm_name, session_id, session_count, state_name):
        raise Exception("Method iCubRESTSubscriberFSM.on_exit_fsm is not implemented!")


class iCubFSM(FSM):

    def __init__(self, JSON_dict=None, JSON_file=None):
        self._app_ = None
        self._actions_ = {}
        FSM.__init__(self, name=self.__class__.__name__, JSON_dict=JSON_dict, JSON_file=JSON_file)

    @property
    def actions(self):
        return self._actions_

    def __on_enter_action__(self):
        current_state = self.getCurrentState()
        self._app_.playAction(self._app_.name + '.' + self.name + '.' + current_state)

    def setApp(self, app: iCubRESTApp):
        self._app_ = app

    def addAction(self, action: iCubFullbodyAction):
        self._actions_[action.name] = action
        self.addState(name=action.name, description=action.description, on_enter_callback=self.__on_enter_action__)
        return action.name

    def importFromJSONDict(self, data):
        name = data.get("name", "")
        states = data.get("states", [])
        transitions = data.get("transitions", [])
        actions = data.get("actions", {})

        for state_data in states:
            self.addState(name=state_data["name"], description=state_data["description"], on_enter_callback=self.__on_enter_action__)

        for transition_data in transitions:
            self.addTransition(trigger=transition_data["trigger"], source=transition_data["source"], dest=transition_data["dest"])

        for action in actions.values():
            self.addAction(iCubFullbodyAction(JSON_dict=action))

        initial_state = data.get("initial_state", FSM.INIT_STATE)
        self._machine_.set_state(initial_state)

    def exportJSONFile(self, filepath):
        data = {
                "name": self._name_,
                "states": self._states_,
                "transitions": self._transitions_,
                "initial_state": self._machine_.initial,
                "session_id": self._session_id_,
                "session_count": self._session_count_,
                "actions": self._actions_
            }
        exportJSONFile(filepath, data)
   
class PyiCubRESTfulClient:

    def __init__(self, host, port, rule_prefix='pyicub'):
        self._host_ = host
        self._port_ = port
        self._rule_prefix_ = rule_prefix
        self._header_ = "http://%s:%d/%s" % (self._host_, self._port_, self._rule_prefix_)

    def __run__(self, robot_name, app_name, target_name, sync, *args, **kwargs):
        data = kwargs
        url = self._header_ + '/' + robot_name + '/' + app_name + '/' + target_name
        if sync:
            url += '?sync'
        res = requests.post(url=url, json=data)
        return res.json()

    def fsm_runStep(self, robot_name, app_name, trigger):
        data = {}
        data['trigger'] = trigger
        res = requests.post(url=self._header_ + '/' + robot_name + '/' + app_name + '/fsm.runStep?sync', json=data)
        return res.json()

    def get_fsm(self, robot_name, app_name):
        res = requests.post(url=self._header_ + '/' + robot_name + '/' + app_name + '/fsm.toJSON?sync', json={})
        return res.json()
        
    def get_version(self):
        res = requests.get(url="http://%s:%d" % (self._host_, self._port_))
        return res.json()['Version']

    def get_robots(self):
        res = requests.get(url=self._header_)
        json_robots = res.json()
        robots = []
        for robot in json_robots:
            robots.append(RESTRobot(json_dict=robot))
        return robots

    def get_apps(self, robot_name):
        res = requests.get(url=self._header_ + '/' + robot_name)
        json_apps = res.json()
        apps = []
        for app in json_apps:
            apps.append(RESTApp(json_dict=app))
        return apps

    def get_services(self, robot_name, app_name):
        res = requests.get(url=self._header_ + '/' + robot_name + '/' + app_name)
        json_services = res.json()
        services = {}
        for name, service_dict in json_services.items():
            services[name] = RESTApp(json_dict=service_dict)
        return services

    def get_robot_actions(self, robot_name):
        res = requests.post(url=self._header_ + '/' + robot_name + '/helper/actions.getActions', json={})
        res = requests.get(res.json())
        return res.json()['retval']

    def play_action(self, robot_name, action_id, sync=True):
        if sync:
            return self.run_target(robot_name, "helper", "actions.playAction", action_id=action_id)
        return self.run_target_async(robot_name, "helper", "actions.playAction", action_id=action_id)

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


class FSMsManager:

    def __init__(self):
        self.__machines__ = {}

    def __get_subclasses__(self, module, base_class):
        subclasses = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, base_class) and obj != base_class:
                subclasses.append(obj)
        return subclasses

    def __instantiate_machines__(self, module):
        try:
            module = importlib.import_module(module)
            clsmembers = self.__get_subclasses__(module, iCubFSM)
            machines = []

            for class_ in clsmembers:
                machines.append( class_() )
            
            return machines
        except (ImportError, AttributeError) as e:
            print(f"Error: {e}")
            print(f"Could not import or instantiate classes for module: {module}")

        return None

    def addFSM(self, machine: iCubFSM, machine_id=None):
        if not machine_id:
            machine_id = machine.name
        if machine_id in self.__machines__.keys():
            raise Exception("An error occurred adding a new FSM! Class name '%s' already present! Please choose different names for each machine class." % machine_id)
        self.__machines__[machine_id] = machine
        return machine_id

    def importFSMsFromModule(self, module):
        machines = self.__instantiate_machines__(module)
        for machine in machines:
            self.addFSM(machine)

    def getFSM(self, machine_id: str):
        if machine_id in self.__machines__.keys():
            return self.__machines__[machine_id]
        raise Exception("machine_id '%s' not found! Please provide a machine identifier previously imported!" % machine_id)

    def getFSMs(self):
        return self.__machines__.keys()

    def exportFSMs(self, path):
        for k, machine in self.__machines__.items():
            machine.exportJSONFile('%s/%s.json' % (path, k))
            machine.draw('%s/%s.png' % (path, k))

