import yarp
from pyicub.core.ports import BufferedReadPort, BufferedPort
from pyicub.core.logger import YarpLogger
from threading import Thread
from random import randint


class Reader:
    def __init__(self):
        self.port = BufferedReadPort("/reader:i", "/writer:o", callback=self.detectMsg)
        self.log  = YarpLogger.getLogger()
    
    def detectMsg(self, bot):
        self.log.debug("READER receiving : " + bot.toString())
        return True


class Writer:
    def __init__(self):
        self.port = BufferedPort()
        self.port.open("/writer:o")
    
    def sendMsg (self, top):
        for i in range (1, top):
            msg = "item " + str(i)
            self.port.write(msg)
            yarp.delay(randint(1,5))



if __name__ == '__main__':

    yarp.Network.init()
    log = YarpLogger.getLogger()
    
    writer = Writer()
    log.debug("init WRITER")
    reader = Reader()
    log.debug("init READER")

    log.debug("start writing")
    writing = Thread(target=writer.sendMsg(10))
    writing.start()
    writing.join()
    log.debug("end writing")

    yarp.Network.fini()