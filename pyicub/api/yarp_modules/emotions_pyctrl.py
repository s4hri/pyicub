# emotions_pyctrl.py

import yarp
from rpc_pyctrl import rpcMod

class emotionsPyCtrl:

    def __init__(self):
        self._rpcMod = rpcMod("/emotionsPyCtrl", "/icub/face/emotions/in")

    def _emoCmd(self, part, emo):
        cmd = yarp.Bottle()
        cmd.clear()
        map(cmd.addString, ["set", part, emo])
        return self._rpcMod.execute(cmd)

    def smile(self):
        self._emoCmd("all", "hap")

    def eb_smile(self):
        self._emoCmd("leb", "hap")
        self._emoCmd("reb", "hap")

    def eb_surprised(self):
        self._emoCmd("leb", "sur")
        self._emoCmd("reb", "sur")


    def surprised(self):
        self._emoCmd("mou", "sur")
        self._emoCmd("leb", "sur")
        self._emoCmd("reb", "sur")

    def neutral(self):
        self._emoCmd("mou", "neu")
        self._emoCmd("leb", "neu")
        self._emoCmd("reb", "neu")

    def sad(self):
        self._emoCmd("mou", "sad")
        self._emoCmd("leb", "sad")
        self._emoCmd("reb", "sad")

    def closingEyes(self):
        self._emoCmd("eli", "sad")

    def cun(self):
        self._emoCmd("leb", "cun")
        self._emoCmd("reb", "cun")

    def angry(self):
        self._emoCmd("all", "ang")

    def evil(self):
        self._emoCmd("all", "evil")

    def close(self):
        self._rpcMod.close()
