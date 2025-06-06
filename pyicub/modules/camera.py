# BSD 2-Clause License
#
# Copyright (c) 2025, Social Cognition in Human-Robot Interaction,
#                     Istituto Italiano di Tecnologia, Genova
#
# All rights reserved.
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

   def __init__(self, robot, side="right", proxy_host=None):
        self.__portImg__ = yarp.BufferedPortImageRgb()
        self.__portImg__.open("/read/"+ side + "_image:o")
        self.__portCamera__ = []
        self._proxy_host_ = proxy_host
        if robot == "icubSim":
           self.__portCamera__ = "/" + robot + "/cam/" + side + "/rgbImage:o"
        elif robot == "icub":
           self.__portCamera__ = "/" + robot + "/camcalib/" + side + "/out"
        yarp.Network.connect(self.__portCamera__, self.__portImg__.getName())

   def getImgRes(self):
      if yarp.Network.isConnected(self.__portCamera__, self.__portImg__.getName()):
         receivedImage = self.__portImg__.read()
         if receivedImage:
            img = yarp.ImageRgb()
            img.copy(receivedImage)
            return [img.width(), img.height()]
      return False

   def getPort(self):
      portcam = yarp.Network.queryName(self.__portCamera__)
      if portcam:
         return portcam.getPort()
      else:
         return False

   def getHost(self):
      if self._proxy_host_:
         return self._proxy_host_
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