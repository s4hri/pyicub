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


from pyicub.requests import iCubRequest, iCubRequestsManager

from flask import Flask, jsonify, request
import threading

class iCubHTTPManager(iCubRequestsManager):

    def __init__(self, rule_prefix="/pyicub", host=None, port=None):
        iCubRequestsManager.__init__(self)
        self._services_ = {}
        self._flaskapp_ = Flask(__name__)
        self._rule_prefix_ = rule_prefix
        self._flaskapp_.add_url_rule(self._rule_prefix_, methods=['GET'], view_func=self.list)
        threading.Thread(target=self._flaskapp_.run, args=(host, port,)).start()

    def shutdown(self):
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
                    res.append(self._requests_[req_id].info())
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
        res = []
        req_id = int(req_id)
        if req_id in self._requests_.keys():
            rule = str(request.url_rule).strip()
            target = rule.split('/')[-2]
            if self._requests_[req_id].target.__name__ == target:
                res = self._requests_[req_id].info()
        return jsonify(res)

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
