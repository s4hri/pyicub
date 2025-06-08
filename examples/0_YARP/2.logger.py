import yarp
from pyicub.core.ports import BufferedReadPort, BufferedPort
from pyicub.core.logger import PyicubLogger, YarpLogger
from threading import Thread
from random import randint

class Reader:
    def __init__(self, logger):
        self.log = logger
        self.port = BufferedReadPort("/reader:i", "/writer:o", callback=self.detectMsg)

    def detectMsg(self, bot):
        self.log.debug("READER receiving : " + bot.toString())
        return True


class Writer:
    def __init__(self, logger):
        self.log = logger
        self.port = BufferedPort()
        self.port.open("/writer:o")
        
    def sendMsg (self, top):
        for i in range (1, top):
            msg = "item " + str(i)
            self.port.write(msg)
            self.log.debug("WRITER sending %s " % msg)
            yarp.delay(randint(1,5))



if __name__ == '__main__':

    yarp.Network.init()
    mylog = YarpLogger.getLogger() 
    #mylog = PyicubLogger.getLogger()

    writer = Writer(logger=mylog)
    mylog.info("init WRITER")
    reader = Reader(logger=mylog)
    mylog.info("init READER")

    mylog.info("start writing")
    writing1 = Thread(target=writer.sendMsg(5))
    writing1.start()
    writing2 = Thread(target=writer.sendMsg(10))
    writing2.start()
    writing1.join()
    writing2.join()

    mylog.info("end writing")

    yarp.Network.fini()