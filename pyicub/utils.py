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

import math
import pyicub
import socket
import json

class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


def vector_distance(v, w):
    t = 0
    for i in range(0, len(v)):
        try:
            t = t + math.pow(v[i]-w[i],2)
        except OverflowError:
            t = t + 0
    return math.sqrt(t)

def norm(v):
    t = 0
    for i in range(0, len(v)):
        try:
            t = t + math.pow(v[i],2)
        except OverflowError:
            t = t + 0
    return math.sqrt(t)

def getPublicMethods(obj):
    object_methods = [method_name for method_name in dir(obj) if callable(getattr(obj, method_name))]
    public_object_methods = list(filter(lambda x: not x.startswith('_'), object_methods))
    return public_object_methods

def getDecoratedMethods(obj, decorator_name):
    decorated_methods = []

    for method_name in dir(obj):
        method = getattr(obj, method_name)
        if callable(method) and hasattr(method, '__call__'):
            decorators = getattr(method, '__decorators__', [])
            if decorator_name in decorators:
                decorated_methods.append(method_name)

    return decorated_methods

def getPyiCubInfo():
    info = {
        'Name': pyicub.__name__,
        'Version': pyicub.__version__,
        'License': pyicub.__license__,
        'Authors': pyicub.__authors__,
        'Emails': pyicub.__emails__,
        'Description': pyicub.__description__
    }
    return info

def firstAvailablePort(host, start_port):
    res = 1
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((host, start_port))
            sock.close()
            break
        except:
            start_port+=1
        sock.close()
    return start_port

def importFromJSONFile(JSON_file):
    with open(JSON_file, encoding='UTF-8') as f:
        data = f.read()
    return json.loads(data)

def exportJSONFile(filepath, obj):
    res = json.dumps(obj, default=lambda o: o.toJSON(), indent=4)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(res)
