import yarp
from pyicub.core.ports import BufferedReadPort, BufferedPort
from pyicub.core.logger import PyicubLogger
from threading import Thread
from random import randint

class Reader:
    def __init__(self):
        self.port = BufferedReadPort("/reader:i", "/writer:o", callback=self.detectMsg)
        self.log = PyicubLogger.getLogger()

    def detectMsg(self, bot):
        self.log.info("READER")
        self.log.debug("READER receiving : " + bot.toString())
        return True


class Writer:
    def __init__(self):
        self.port = BufferedPort()
        self.port.open("/writer:o")
        self.log = PyicubLogger.getLogger()

    def sendMsg (self, top):
        for i in range (1, top):
            msg = "item " + str(i)
            self.log.info("WRITER")
            self.port.write(msg)
            self.log.debug("WRITER sending %s " % msg)
            yarp.delay(randint(1,5))



if __name__ == '__main__':

    yarp.Network.init()
    log = PyicubLogger.getLogger()
    log.configure(PyicubLogger.LOGGING_LEVEL, PyicubLogger.FORMAT)
    writer = Writer()
    log.info("init WRITER")
    reader = Reader()
    log.info("init READER")

    log.info("start writing")
    writing1 = Thread(target=writer.sendMsg(50))
    writing1.start()
    writing2 = Thread(target=writer.sendMsg(100))
    writing2.start()
    writing1.join()
    writing2.join()

    log.info("end writing")

    yarp.Network.fini()