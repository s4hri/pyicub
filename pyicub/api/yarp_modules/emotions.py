# emotions_pyctrl.py

import yarp
from pyicub.api.yarp_classes.Rpc import RpcClient


class emotionsPyCtrl:

    def __init__(self):
        self.__rpc__ = RpcClient("/icub/face/emotions/in")

    def __emoCmd__(self, part, emo):
        cmd = yarp.Bottle()
        cmd.clear()
        map(cmd.addString, ["set", part, emo])
        return self.__rpc__.execute(cmd)

    def smile(self):
        self.__emoCmd__("all", "hap")

    def eb_smile(self):
        self.__emoCmd__("leb", "hap")
        self.__emoCmd__("reb", "hap")

    def eb_surprised(self):
        self.__emoCmd__("leb", "sur")
        self.__emoCmd__("reb", "sur")


    def surprised(self):
        self.__emoCmd__("mou", "sur")
        self.__emoCmd__("leb", "sur")
        self.__emoCmd__("reb", "sur")

    def neutral(self):
        self.__emoCmd__("mou", "neu")
        self.__emoCmd__("leb", "neu")
        self.__emoCmd__("reb", "neu")

    def sad(self):
        self.__emoCmd__("mou", "sad")
        self.__emoCmd__("leb", "sad")
        self.__emoCmd__("reb", "sad")

    def closingEyes(self):
        self.__emoCmd__("eli", "sad")

    def cun(self):
        self.__emoCmd__("leb", "cun")
        self.__emoCmd__("reb", "cun")

    def angry(self):
        self.__emoCmd__("all", "ang")

    def evil(self):
        self.__emoCmd__("all", "evil")

    def close(self):
        self.__rpc__.close()
