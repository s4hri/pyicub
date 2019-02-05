import yarp
from rpc_pyctrl import rpcMod

class speechPyCtrl:

    def __init__(self):
        self._rpcMod = rpcMod("/iSpeechPyCtrl", "/icub/speech:rpc")

    def _sayCmd(self, something):
        cmd = yarp.Bottle()
        cmd.clear()
        map(cmd.addString, ["say", something])
        return self._rpcMod.execute(cmd)

    def say(self, something):
        self._sayCmd(something)

    def __del__(self):
        try:
            del self._rpcMod
        except:
	           pass
