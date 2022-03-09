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
import time
icub = iCub()

for j in range(100):
    # get number of face detected
    faces     = icub.facelandmarks.getFaces()
    if faces > 0:
        for i in range(faces):
            # for each face get center eyes
            center_eye = icub.facelandmarks.getCenterEyes(i)
            print("face %i - [x: %s , y: %s ]" % (i+1, center_eye[0], center_eye[1]))
    else:
        # no face detected
        print("no face detected")

    time.sleep(0.1)
