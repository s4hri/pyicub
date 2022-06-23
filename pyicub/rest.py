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

from pyicub.requests import iCubRequest
from pyicub.utils import SingletonMeta, getPyiCubInfo
from flask import Flask, jsonify, request
import requests
import json

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
        self._header_ = "http://%s:%s" % (self._host_, self._port_)
        self._flaskapp_.add_url_rule("/", methods=['GET'], view_func=self.info)
        self._flaskapp_.add_url_rule("/%s" % self._rule_prefix_, methods=['GET'], view_func=self.list_robots)
        self._flaskapp_.add_url_rule("/%s/register" % self._rule_prefix_, methods=['POST'], view_func=self.remote_register)

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


    def wrapper_target(self, *args, **kwargs):
        rule = str(request.url_rule).strip()
        if request.method == 'GET':
            res = json.dumps(self._services_[rule], default=lambda o: o.__dict__, indent=4)
            return res
        elif request.method == 'POST':
            return self.process_target(self._services_[rule])

    def process_target(self, service):
        url = service.url
        data = request.get_json(force=True)
        if 'sync' in request.args:
            url+="?sync"
        res = requests.post(url=url, json=data)
        return res.content

    def info(self):
        return jsonify(getPyiCubInfo())

    def list_apps(self, robot_name):
        return jsonify(list(self._apps_[robot_name].values()))

    def list_robots(self):
        return jsonify(list(self._robots_.values()))

    def list_services(self, robot_name, app_name):
        return jsonify(self._app_services_[robot_name][app_name])

    def remote_register(self):
        res = request.get_json(force=True)
        self.register(robot_name=res["robot_name"], app_name=res["app_name"], target_name=res["target_name"], target=res["target"],  target_signature=res["target_signature"], host=res["host"], port=res["port"])
        return res

    def register(self, robot_name, app_name, target_name, target, target_signature, host, port):
        robot_rule = "/" + self._rule_prefix_ + "/" + robot_name
        app_rule = robot_rule + "/" + app_name
        target_rule = app_rule + "/" + target_name

        if not robot_name in self._app_services_.keys():
            self._app_services_[robot_name] = {}
            self._apps_[robot_name] = {}
        robot = { 'name': robot_name,
                  'url_local': self._header_ + robot_rule,
                  'url_remote': None
                }
        self._robots_[robot_name] = robot
        if not (self._host_ == host and self._port_ == port):
            robot['url_remote']  = "http://%s:%d" % (host, port) + robot_rule
        self._flaskapp_.add_url_rule("/%s/<robot_name>" % self._rule_prefix_, methods=['GET'], view_func=self.list_apps)
        self._app_services_[robot_name][app_name] = []
        app = { 'name': app_name, 
                    'url_local': self._header_ + app_rule,
                    'url_remote': None
              }
        if not (self._host_ == host and self._port_ == port):
            app['url_remote']  = "http://%s:%d" % (host, port) + app_rule
        self._apps_[robot_name][app_name] = app
        self._flaskapp_.add_url_rule("/%s/<robot_name>/<app_name>" % self._rule_prefix_, methods=['GET'], view_func=self.list_services)
        self._flaskapp_.add_url_rule("/%s/<robot_name>/<app_name>/requests" % self._rule_prefix_, methods=['GET'], view_func=self.app_requests)
        self._flaskapp_.add_url_rule("/%s/<robot_name>/<app_name>/<target_name>/<req_id>" % (self._rule_prefix_), methods=['GET'], view_func=self.req_info)
        service = { 'name': target_name,
                    'url_local': self._header_ + target_rule,
                    'url_remote': None
                  }
        if not (self._host_ == host and self._port_ == port):
            service['url_remote'] = "http://%s:%d" % (host, port) + target_rule

        self._app_services_[robot_name][app_name].append(service)
        
        self._flaskapp_.add_url_rule("/%s/%s/%s/%s" % (self._rule_prefix_, robot_name, app_name, target_name), methods=['GET', 'POST'], view_func=self.wrapper_target)
        service_url = "http://%s:%d/%s/%s/%s/%s" % (host, port, self._rule_prefix_, robot_name, app_name, target_name)
        self._services_[target_rule] = iCubRESTService(name=target_name,
                                                robot_name=robot_name,
                                                app_name=app_name,
                                                url=service_url,
                                                target=target,
                                                signature=target_signature)

    def app_requests(self, robot_name, app_name):
        url = str(request.url).strip()
        params = url.split("?")
        if len(params) > 1:
            params = params[1]

        if app_name in self._apps_[robot_name].keys():
            app = self._apps_[robot_name][app_name]
            res = requests.get('%s/requests?%s' % (app['url_remote'], params))
            return jsonify(res.json())

    def req_info(self, req_id, robot_name=None, app_name=None, target_name=None):
        if app_name in self._apps_[robot_name].keys():
            app = self._apps_[robot_name][app_name]
            res = requests.get('%s/%s/%s' % (app['url_remote'], target_name, req_id))
            return jsonify(res.json())


class iCubRESTManager(iCubRESTServer):

    def __init__(self, icubrequestmanager, rule_prefix, host, port, proxy_host, proxy_port):
        iCubRESTServer.__init__(self, rule_prefix, host, port)
        self._proxy_host_ = proxy_host
        self._proxy_port_ = proxy_port
        self._requests_ = {}
        self.request_manager = icubrequestmanager
        try:
            requests.get('http://%s:%s/%s' % (self._proxy_host_, self._proxy_port_, self._rule_prefix_))
        except:
            self.request_manager.logger.error("An issue occurred while connecting to the iCubRESTServer. Are you sure is the server running at %s:%d ?" % (self._proxy_host_, self._proxy_port_))
    

    def app_requests(self, robot_name, app_name):
        reqs = []
        if 'id' in request.args:
            req_id = request.args['id']
            return self.req_info(req_id)
        elif 'pending' in request.args:
            return self.pending_requests()
        for req_id, req in self._requests_.items():
            if robot_name == req['robot_name'] and app_name == req['app_name']:
                reqs.append(req['request'].info())
        return jsonify(reqs)

    def req_info(self, req_id, robot_name=None, app_name=None, target_name=None):
        if req_id in self._requests_.keys():
            return jsonify(self._requests_[req_id]['request'].info())
        return jsonify([])
    

    def all_requests(self):
        reqs = []
        for req in self._requests_.values():
            reqs.append(req['request'].info())
        return jsonify(reqs)

    def pending_requests(self):
        reqs = []
        for req in self._requests_.values():
            if req['request'].status == "RUNNING":
                reqs.append(req['request'].info())
        return jsonify(reqs)

    def process_target(self, service):
        res = request.get_json(force=True)
        kwargs =  res
        if 'sync' in request.args:
            res = service.target(**kwargs)
            return jsonify(res)
        req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST, target=service.target, name=service.name, prefix=service.url)
        
        self._requests_[req.req_id] = {'robot_name': service.robot_name,
                                       'app_name': service.app_name,
                                       'request': req}
        self.request_manager.run_request(req, False, **kwargs)
        return jsonify(req.req_id)

    def register_target(self, robot_name, app_name, target_name, target, target_signature):
        self.register(robot_name, app_name, target_name, target, target_signature, self._host_, self._port_)
        data = { "robot_name": robot_name,
                 "app_name": app_name,
                 "target_name": target_name,
                 "target": None,
                 "target_signature": target_signature,
                 "host": self._host_,
                 "port": self._port_ }

        res = requests.post('http://%s:%s/%s/register' % (self._proxy_host_, self._proxy_port_, self._rule_prefix_), json=data)
        return res.content



