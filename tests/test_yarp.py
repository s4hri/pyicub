#   Copyright (C) 2021  Davide De Tommaso
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>

import unittest
import sys
import yarp
import time

from pyicub.core.BufferedPort import BufferedPort, BufferedReadPort, BufferedWritePort
from pyicub.core.Rpc import RpcClient

if yarp.Network.checkNetwork(1.0) is False:
    yarp.Network.setLocalMode(True)
yarp.Network.init()

class TestYarpMethods(unittest.TestCase):

    def test_01_bufferedReadPort(self):
        port = BufferedReadPort('/in', '/out')
        port.read(shouldWait=False)

    def test_02_bufferedWritePort(self):
        port = BufferedWritePort('/out', '/in')
        port.write("test_02_bufferedWritePort")

    def test_03_bufferedReadWrite(self):
        writeport = BufferedPort()
        readport = BufferedPort()
        writeport.open('/out')
        readport.open('/in')
        readport.setStrict()
        yarp.Network.connect('/out', '/in')
        msg = "test_03_bufferedReadWrite"
        writeport.write(msg, forceStrict=True)
        self.assertEqual(readport.read().toString(), msg)

    def test_04_rpc(self):
        rpc = RpcClient("/root")

if __name__ == '__main__':
    unittest.main()
    yarp.Network.fini()
