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

from pyicub.helper import iCub

icub = iCub()
icub.gaze.lookAtFixationPoint(-1.0, -0.5, 1.0, waitMotionDone=False)
icub.gaze.waitMotionOnset()

icub.gaze.lookAtFixationPoint(-1.0, -0.2, 0.5)
icub.gaze.lookAtFixationPoint(-1.0, 0.2, 0.1)
icub.gaze.lookAtAbsAngles(0.0, 0.0, 0.0)

icub.close()