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

import yarp

from pyicub.modules.emotions import emotionsPyCtrl
from pyicub.core.logger import YarpLogger

yarp.Network.init()
log = YarpLogger.getLogger()

robot = "icubSim"
emo = emotionsPyCtrl(robot)

emo.smile()
yarp.delay(2)
emo.surprised()
yarp.delay(2)
emo.neutral()
yarp.delay(2)
emo.sad()
yarp.delay(2)
emo.angry()
yarp.delay(2)
emo.evil()
yarp.delay(2)
emo.closingEyes()
yarp.delay(2)
emo.openingEyes()
yarp.delay(2)
emo.smile()

log.info("END")