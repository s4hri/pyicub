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
from pyicub.helper import iCub

yarp.Network.init()

DOWN = [0.0, -30.0, 3.0]
ZERO = [0.0, 0.0, 3.0]
UP = [0.0, 30.0, 3.0]

def af1(values):
    lastread = values[-1].split(' ')
    if abs(ZERO[1] - float(lastread[1])) < 2:
        return True
    return False

def cb1():
    print("Watching at ZERO detected!")

icub = iCub()

icub.portmonitor("/iKinGazeCtrl/angles:o", activate_function=af1, callback=cb1)

icub.gaze.lookAtAbsAngles(UP[0], UP[1], UP[2])

for _ in range(0,3):
    icub.gaze.lookAtAbsAngles(DOWN[0], DOWN[1], DOWN[2])
    icub.gaze.lookAtAbsAngles(UP[0], UP[1], UP[2])

icub.gaze.lookAtAbsAngles(0.0, 0.0, 0.0)
icub.close()
