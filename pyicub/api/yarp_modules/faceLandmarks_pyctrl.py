import yarp
from rpc_pyctrl import rpcMod
from port_pyctrl import yarpReadPortPyCtrl

class faceLandmarksPyCtrl:

    def __init__(self):
        self._rpcMod = rpcMod("/faceLandmarksPyCtrl", "/faceLandmarks/rpc:i")
        self._port_landmarks = yarpReadPortPyCtrl("/faceLandmarks/landmarks:o", "/faceLandmarksPyCtrl/landmarks:i")

    def sendCmd(self, cmd, option):
        btl = yarp.Bottle()
        btl.clear()
        map(btl.addString, [cmd, option])
        return self._rpcMod.execute(btl)

    def getLandmarks(self):
        btl = self._port_landmarks.read_nowait()        
        if btl is None:
            return None
        s = btl.toString().split("(")[1].split(")")[0].split(" ")
        return map(int, s)

    def close(self):
        self._rpcMod.close()
