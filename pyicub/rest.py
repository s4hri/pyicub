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

from flask import Flask, jsonify, request
import threading
import json
import inspect

class iCubRESTService:

    def __init__(self, name, url, target, doc, signature):

        self.name = name
        self.url = url
        self.target = target
        self.doc = doc
        self.signature = signature

class iCubRESTManager:

    def __init__(self, icubrequestmanager, rule_prefix="/pyicub", host=None, port=None):
        self.request_manager = icubrequestmanager
        self._services_ = {}
        self._requests_ = {}
        self._flaskapp_ = Flask(__name__)
        self._rule_prefix_ = rule_prefix
        self._flaskapp_.add_url_rule(self._rule_prefix_, methods=['GET'], view_func=self.list)
        self._flaskapp_.add_url_rule("%s/requests/<req_id>" % self._rule_prefix_, methods=['GET'], view_func=self.req_info)
        self._flaskapp_.add_url_rule("%s/requests/pending" % self._rule_prefix_, methods=['GET'], view_func=self.pending_requests)
        self._flaskapp_.add_url_rule("%s/requests/all" % self._rule_prefix_, methods=['GET'], view_func=self.all_requests)
        threading.Thread(target=self._flaskapp_.run, args=(host, port,)).start()

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
            res = request.get_json(force=True)
            args = tuple(res.values())
            kwargs =  res
            if 'sync' in request.args:
                res = self._services_[rule].target(**kwargs)
                return jsonify(res)
            req = self.request_manager.create(timeout=iCubRequest.TIMEOUT_REQUEST, target=self._services_[rule].target, name=rule)
            self._requests_[req.req_id] = req
            self.request_manager.run_request(req, False, **kwargs)
            return jsonify(req.req_id)

    def req_info(self, req_id):
        res = self._requests_[int(req_id)].info()
        return jsonify(res)

    def list(self):
        return jsonify(list(self._services_.keys()))

    def all_requests(self):
        reqs = []
        for req in self._requests_.values():
            reqs.append(req.info())
        return jsonify(reqs)

    def pending_requests(self):
        reqs = []
        for req in self._requests_.values():
            if req.status == "RUNNING":
                reqs.append(req.info())
        return jsonify(reqs)

    def register(self, target, rule_prefix=None):
        if rule_prefix:
            rule = "%s/%s/%s" % (self._rule_prefix_, rule_prefix, target.__name__)
        else:
            rule = "%s/%s" % (self._rule_prefix_, target.__name__)
        self._flaskapp_.add_url_rule(rule, methods=['GET', 'POST'], view_func=self.wrapper_target)
        self._services_[rule] = iCubRESTService(name=target.__name__, 
                                                url=rule, 
                                                target=target,
                                                doc=target.__doc__,
                                                signature=str(inspect.signature(target)))