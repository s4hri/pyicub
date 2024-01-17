#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import yarp

class cameraPyCtrl:

   def __init__(self, robot, side="right"):
        self.__portImg__ = yarp.BufferedPortImageRgb()
        self.__portImg__.open("/read/image:o")
        self.__portCamera__ = []
        if robot == "icubSim":
           self.__portCamera__ = "/" + robot + "/cam/" + side
        elif robot == "icub":
           self.__portCamera__ = "/" + robot + "/camcalib/" + side + "/out"
        yarp.Network.connect(self.__portCamera__, self.__portImg__.getName())

   def getImgRes(self):
      if yarp.Network.isConnected(self.__portCamera__, self.__portImg__.getName()):
         receivedImage = self.__portImg__.read()
         img = yarp.ImageRgb()
         img.copy(receivedImage)
         return [img.width(), img.height()]
      else:
         return False

   def getPort(self):
      portcam = yarp.Network.queryName(self.__portCamera__)
      if portcam:
         return portcam.getPort()
      else:
         return False

   def getHost(self):
      portcam = yarp.Network.queryName(self.__portCamera__)
      if portcam:
         return portcam.getHost()
      else:
         return False

   def getURI(self):
      port = self.getPort()
      host = self.getHost()
      if port and host:
         return "http://" + str(host) + ":" + str(port) + "/?action"
      return None

   def __del__(self):
      yarp.Network.disconnect(self.__portCamera__, self.__portImg__.getName())
      self.__portImg__.interrupt()
      self.__portImg__.close()