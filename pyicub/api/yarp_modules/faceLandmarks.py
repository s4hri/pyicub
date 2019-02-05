import yarp
from pyicub.api.yarp_classes.Rpc import RpcClient
from pyicub.api.yarp_classes.BufferedPort import BufferedReadPort

class faceLandmarksPyCtrl:

    def __init__(self):
        self.__rpc__ = RpcClient("/faceLandmarksPyCtrl", "/faceLandmarks/rpc:i")
        self.__port_landmarks__ = BufferedReadPort("/faceLandmarks/landmarks:o", "/faceLandmarksPyCtrl/landmarks:i")

    def sendCmd(self, cmd, option):
        btl = yarp.Bottle()
        btl.clear()
        map(btl.addString, [cmd, option])
        return self.__rpc__.execute(btl)

    def getLandmarks(self):
        btl = self.__port_landmarks__.read(shouldWait=False)
        if btl is None:
            return None
        s = btl.toString().split("(")[1].split(")")[0].split(" ")
        return map(int, s)

    def close(self):
        self.__rpc__.close()
