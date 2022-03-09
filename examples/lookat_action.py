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

from pyicub.helper import iCub, GazeMotion, iCubFullbodyAction

icub = iCub()

g1 = GazeMotion(lookat_method="lookAtFixationPoint")
g1.addCheckpoint([-1.0, -0.5, 1.0])
g1.addCheckpoint([-1.0, -0.2, 0.5])
g1.addCheckpoint([-1.0, 0.2, 0.1])

g2 = GazeMotion(lookat_method="lookAtAbsAngles")
g2.addCheckpoint([0.0, 0.0, 0.0, False, 1.5])

action = iCubFullbodyAction()
step1 = action.addStep()
step2 = action.addStep()
step1.setGazeMotion(g1)
step2.setGazeMotion(g2)

action.exportJSONFile('json/lookat.json')

imported_action = iCubFullbodyAction(JSON_file='json/lookat.json')
icub.play(imported_action)
