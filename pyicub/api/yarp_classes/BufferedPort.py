import yarp

class BufferedPort:

    def __init__(self):
        self.__port__ = yarp.BufferedPortBottle()

    def open(self, port):
        self.__port__.open(port)

    def read(self, shouldWait=True):
        return self.__port__.read(shouldWait)

    def lastRead(self):
        return self.__port__.lastRead()

    def write(self, forceStrict=False):
        self.__port__.write(forceStrict)

    def setStrict(self):
        self.__port__.setStrict()

    def prepare(self):
        btl = self.__port__.prepare()
        btl.clear()
        return btl

    def __del__(self):
        self.__port__.interrupt()
        self.__port__.close()

class BufferedReadPort(BufferedPort):

    def __init__(self, port_name, port_src):
        BufferedPort.__init__(self)
        self.__port_name__ = port_name
        self.__port_src__ = port_src
        self.open(self.__port_name__)
        yarp.Network.connect(self.__port_name__, self.__port_src__)

    def __del__(self):
        yarp.Network.disconnect(self.__port_name__, self.__port_src__)


class BufferedWritePort(BufferedPort):

    def __init__(self, port_name, port_dst):
        BufferedPort.__init__(self)
        self.__port_name__ = port_name
        self.__port_dst__ = port_dst
        self.__port__.open(self.__port_dst__)
        yarp.Network.connect(self.__port_name__, self.__port_dst__)

    def __del__(self):
        yarp.Network.disconnect(self.__port_name__, self.__port_dst__)
