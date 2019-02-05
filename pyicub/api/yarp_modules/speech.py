import yarp
from pyicub.api.yarp_classes.Rpc import RpcClient

class speechPyCtrl:

    def __init__(self):
        self.__rpc__ = RpcClient("/iSpeechPyCtrl", "/icub/speech:rpc")

    def __sayCmd__(self, something):
        cmd = yarp.Bottle()
        cmd.clear()
        map(cmd.addString, ["say", something])
        return self.__rpc__.execute(cmd)

    def say(self, something):
        self.__sayCmd__(something)

    def close(self):
        self.__rpc__.close()
