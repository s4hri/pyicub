# BSD 2-Clause License
#
# Copyright (c) 2025, Social Cognition in Human-Robot Interaction,
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

"""Unit tests for the pyicub.yarp helpers and wrappers.

These tests use a lightweight fake yarp module to validate the pure-Python
behavior of the recently added YARP wrapper utilities without requiring a
running YARP network or robot hardware.
"""

from __future__ import annotations

import importlib
import sys
import types

import pytest


def _create_fake_yarp() -> types.SimpleNamespace:
    """Build a minimal fake yarp module for unit testing."""

    class _BottleItem:
        def __init__(self, value):
            self.value = value

        def asString(self):
            return str(self.value)

        def asFloat64(self):
            return float(self.value)

        def asVocab32(self):
            if isinstance(self.value, int):
                return self.value
            try:
                return int(self.value)
            except (ValueError, TypeError):
                return 0

    class Bottle:
        def __init__(self, tokens=None, props=None):
            self.tokens = list(tokens) if tokens else []
            self.props = dict(props or {})

        def addString(self, token):
            self.tokens.append(str(token))

        def addVocab32(self, vocab):
            self.tokens.append(int(vocab))

        def clear(self):
            self.tokens.clear()
            self.props.clear()

        def size(self):
            return len(self.tokens)

        def get(self, idx):
            return _BottleItem(self.tokens[idx])

        def toString(self):
            return " ".join(str(t) for t in self.tokens)

        def check(self, key):
            return key in self.props

        def find(self, key):
            return _BottleItem(self.props[key])

    class RpcClient:
        def __init__(self):
            self.port_name = None
            self.written = []
            self.response_tokens = ["ok"]
            self.should_fail = False

        def open(self, name):
            self.port_name = name
            return True

        def close(self):
            self.port_name = None

        def write(self, bottle_out, bottle_in):
            self.written.append(bottle_out.toString())
            if self.should_fail:
                return False

            bottle_in.clear()
            for token in self.response_tokens:
                bottle_in.addString(token)
            return True

    class Port:
        def __init__(self):
            self.open_name = None
            self.closed = False

        def open(self, name):
            self.open_name = name
            return True

        def close(self):
            self.closed = True

    class Network:
        init_calls = 0
        fini_calls = 0
        connections = []
        disconnections = []

        @classmethod
        def init(cls):
            cls.init_calls += 1

        @classmethod
        def fini(cls):
            cls.fini_calls += 1

        @classmethod
        def checkNetwork(cls):
            return cls.init_calls > cls.fini_calls

        @classmethod
        def connect(cls, src, dst):
            cls.connections.append((src, dst))
            return True

        @classmethod
        def disconnect(cls, src, dst):
            cls.disconnections.append((src, dst))
            return True

    class RFModule:
        def __init__(self):
            self.attached_port = None

        def attach(self, port):
            self.attached_port = port
            return True

        def runModule(self):
            return True

    class ResourceFinder:
        def __init__(self, data=None):
            self.data = dict(data or {})

        def configure(self, argv=None):
            return True

        def check(self, key):
            return key in self.data

        def find(self, key):
            return _BottleItem(self.data[key])

    def createVocab32(a, b, c, d):
        return (a << 24) + (b << 16) + (c << 8) + d

    return types.SimpleNamespace(
        Bottle=Bottle,
        RpcClient=RpcClient,
        Port=Port,
        Network=Network,
        RFModule=RFModule,
        ResourceFinder=ResourceFinder,
        createVocab32=createVocab32,
    )


_MODULES = [
    "pyicub.yarp.bottle",
    "pyicub.yarp.port",
    "pyicub.yarp.network",
    "pyicub.yarp.client",
    "pyicub.yarp.server",
    "pyicub.yarp.vocab",
]


@pytest.fixture
def yarp_env(monkeypatch):
    """Provide a fake yarp module and freshly reloaded pyicub.yarp modules."""

    for mod in _MODULES + ["yarp"]:
        sys.modules.pop(mod, None)

    fake_yarp = _create_fake_yarp()
    monkeypatch.setitem(sys.modules, "yarp", fake_yarp)

    modules = {
        "bottle": importlib.import_module("pyicub.yarp.bottle"),
        "port": importlib.import_module("pyicub.yarp.port"),
        "network": importlib.import_module("pyicub.yarp.network"),
        "client": importlib.import_module("pyicub.yarp.client"),
        "server": importlib.import_module("pyicub.yarp.server"),
        "vocab": importlib.import_module("pyicub.yarp.vocab"),
    }

    yield types.SimpleNamespace(fake_yarp=fake_yarp, **modules)


def test_bottle_helper_roundtrip(yarp_env):
    helper = yarp_env.bottle.YarpBottleHelper
    source = yarp_env.fake_yarp.Bottle(tokens=["hello", "world", 5])

    tokens = helper.bottle_to_list(source)
    assert tokens == ["hello", "world", "5"]
    assert helper.bottle_to_string(source) == "hello world 5"

    updated = helper.list_to_bottle(["new", "values"], source)
    assert updated is source
    assert updated.toString() == "new values"


def test_base_yarp_port_open_and_close(yarp_env):
    class DummyPort(yarp_env.port.BaseYarpPort):
        def _create_port(self):
            return yarp_env.fake_yarp.Port()

    port = DummyPort("local")
    assert port.port_name == "/local"
    assert port.open() is True
    assert port.is_open is True
    assert port.port.open_name == "/local"

    port.close()
    assert port.is_open is False
    assert port.port.closed is True


def test_yarp_network_context_manager(yarp_env):
    network = yarp_env.network.YarpNetwork()

    assert network.is_initialized is False
    with network as ctx:
        assert ctx.is_initialized is True
        assert yarp_env.fake_yarp.Network.init_calls == 1
        assert ctx.is_available() is True

    assert network.is_initialized is False
    assert yarp_env.fake_yarp.Network.fini_calls == 1


def test_rpc_client_send_and_disconnect(yarp_env):
    class DummyClient(yarp_env.client.BaseRpcClient):
        def _create_port(self):
            # Use a port with a deterministic reply
            rpc = yarp_env.fake_yarp.RpcClient()
            rpc.response_tokens = ["pong"]
            return rpc

    client = DummyClient("/rpc/client", "/rpc/server")

    assert client.open() is True
    assert client.connect() is True
    assert client.is_connected is True

    response = client.send("ping", "42")
    assert response == "pong"
    assert yarp_env.fake_yarp.Network.connections == [("/rpc/client", "/rpc/server")]

    client.close()
    assert yarp_env.fake_yarp.Network.disconnections == [("/rpc/client", "/rpc/server")]
    assert client.is_connected is False


def test_rpc_client_send_without_open_raises(yarp_env):
    class DummyClient(yarp_env.client.BaseRpcClient):
        def _create_port(self):
            return yarp_env.fake_yarp.RpcClient()

    client = DummyClient("/rpc/client", "/rpc/server")
    with pytest.raises(RuntimeError):
        client.send("ping")


def test_rfmodule_standard_commands_and_custom_handler(yarp_env):
    class DemoServer(yarp_env.server.BaseRFModuleServer):
        def _get_default_module_name(self):
            return "/demo"

        def handle_command(self, cmd, tokens, reply):
            if cmd == "echo" and len(tokens) > 1:
                reply.addString(tokens[1])
                return True
            return False

    rf = yarp_env.fake_yarp.ResourceFinder({"name": "demo_mod", "period": 0.25})
    server = DemoServer()
    assert server.configure(rf) is True
    assert server.module_name == "/demo_mod"
    assert server.period == 0.25
    assert server._handle_port.open_name == "/demo_mod/rpc"

    # Help command returns usage
    reply = yarp_env.fake_yarp.Bottle()
    keep_running = server.respond(yarp_env.fake_yarp.Bottle(tokens=["help"]), reply)
    assert keep_running is True
    assert "help" in reply.toString()

    # Period command updates state
    reply = yarp_env.fake_yarp.Bottle()
    server.respond(yarp_env.fake_yarp.Bottle(tokens=["period", "0.5"]), reply)
    assert server.period == 0.5
    assert "0.5" in reply.toString()

    # Custom command handled by subclass
    reply = yarp_env.fake_yarp.Bottle()
    server.respond(yarp_env.fake_yarp.Bottle(tokens=["echo", "hi"]), reply)
    assert reply.toString() == "hi"

    # Vocab-based quit stops the module
    reply = yarp_env.fake_yarp.Bottle()
    quit_cmd = yarp_env.fake_yarp.Bottle(tokens=[yarp_env.vocab.VOCAB_QUIT])
    keep_running = server.respond(quit_cmd, reply)
    assert keep_running is False
    assert reply.toString() == "bye"
