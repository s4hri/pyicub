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

from pyicub.helper import iCub, GazeMotion, iCubFullbodyAction, PyiCubCustomCall

icub = iCub()

a = PyiCubCustomCall(target="gaze.lookAtAbsAngles", args=(0.0, 15.0, 0.0,))
b = PyiCubCustomCall(target="emo.neutral")

c = PyiCubCustomCall(target="gaze.lookAtAbsAngles", args=(0.0, 0.0, 0.0,))
d = PyiCubCustomCall(target="emo.smile")

action = iCubFullbodyAction()
step1 = action.addStep()
step2 = action.addStep()

step1.addCustomCall(a)
step1.addCustomCall(b)
step2.addCustomCall(c)
step2.addCustomCall(d)

action.exportJSONFile('json/custom.json')

imported_action = iCubFullbodyAction(JSON_file='json/custom.json')
icub.play(imported_action)
