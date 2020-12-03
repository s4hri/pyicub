#   Copyright (C) 2019  Davide De Tommaso
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
import sys
sys.path.append('../../')

from pyicub.api.iCubHelper import iCub, iCubWatcher, ROBOT_TYPE

yarp.Network.init()

DOWN = [0.0, -30.0, 3.0]
ZERO = [0.0, 0.0, 3.0]
UP = [0.0, 30.0, 3.0]
single_event_detected = False

def af1(values):
    lastread = values[-1].split(' ')
    if abs(ZERO[1] - float(lastread[1])) < 2:
        return True
    return False

def cb1():
    global single_event_detected
    if not single_event_detected:
        print("Watching at ZERO detected!")
        single_event_detected = True


def lookat(icub, position):
    p = yarp.Vector(3)
    p.set(0, position[0]) # Azimuth
    p.set(1, position[1]) # Elevation
    p.set(2, position[2]) # Vergence
    icub.gaze.getIGazeControl().lookAtAbsAnglesSync(p)
    icub.gaze.getIGazeControl().waitMotionDone(timeout=5.0)

icub = iCub(ROBOT_TYPE.ICUB, logtype="DEBUG")

watch_zero = iCubWatcher("/iKinGazeCtrl/angles:o", activate_function=af1, callback=cb1)

lookat(icub, UP)
watch_zero.start()
for _ in range(0,3):
    single_event_detected = False
    lookat(icub, DOWN)
    single_event_detected = False
    lookat(icub, UP)

watch_zero.stop()