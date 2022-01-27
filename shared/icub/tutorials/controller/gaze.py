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

from pyicub.controllers.gaze import GazeController
from pyicub.core.logger import YarpLogger

from pyicub.helper import iCub

yarp.Network.init()
log = YarpLogger.getLogger()

robot = "icubSim"
igaze = GazeController(robot).__IGazeControl__

icub = iCub(configuration_file="robot_configuration.yaml")
icub.gaze.lookAtAbsAngles( 5.0, -0.5, 1.0, waitMotionDone=True)
icub.gaze.lookAtAbsAngles(-5.0, -0.5, 1.0, waitMotionDone=True)
icub.gaze.lookAtAbsAngles( 5.0, -0.5, 1.0, waitMotionDone=True)
icub.gaze.lookAtAbsAngles(-5.0, -0.5, 1.0, waitMotionDone=True)

angles_right = yarp.Vector(3)
angles_right.set(0, 5.0)
angles_right.set(1, 0.0)
angles_right.set(2, 1.0)
angles_left = yarp.Vector(3)
angles_left.set(0, -5.0)
angles_left.set(1, 0.0)
angles_left.set(2, 1.0)

icub.gaze.IGazeControl.lookAtAbsAngles(angles_right)
icub.gaze.IGazeControl.waitMotionDone()
icub.gaze.IGazeControl.lookAtAbsAngles(angles_left)
icub.gaze.IGazeControl.waitMotionDone()
icub.gaze.IGazeControl.lookAtAbsAngles(angles_right)
icub.gaze.IGazeControl.waitMotionDone()
icub.gaze.IGazeControl.lookAtAbsAngles(angles_left)
icub.gaze.IGazeControl.waitMotionDone()