import unittest
import sys
import yarp

sys.path.append('../../../')
from pyicub.api.yarp_classes.BufferedPort import BufferedPort, BufferedReadPort, BufferedWritePort
from pyicub.api.yarp_classes.Rpc import RpcClient

yarp.Network.init()
yarp.Network.setLocalMode(True)

class TestYarpMethods(unittest.TestCase):

    def test_01_bufferedReadPort(self):
        port = BufferedReadPort('/in', '/out')
        port.read(shouldWait=False)

    def test_02_bufferedWritePort(self):
        port = BufferedWritePort('/out', '/in')
        btl = port.prepare()
        btl.addString("test_02_bufferedWritePort")
        port.write()

    def test_03_bufferedReadWrite(self):
        writeport = BufferedPort()
        readport = BufferedPort()
        writeport.open('/out')
        readport.open('/in')
        readport.setStrict()
        yarp.Network.connect('/out', '/in')
        btl = writeport.prepare()
        msg = "test_03_bufferedReadWrite"
        btl.fromString(msg)
        writeport.write(True)
        self.assertEqual(readport.read().toString(), msg)

    def test_04_rpc(self):
        rpc = RpcClient("/root")

if __name__ == '__main__':
    unittest.main()
    yarp.Network.fini()
