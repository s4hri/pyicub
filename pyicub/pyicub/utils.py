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

import math

class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


def vector_distance(v, w):
    t = 0
    for i in range(0, len(v)):
        try:
            t = t + math.pow(v[i]-w[i],2)
        except OverflowError:
            t = t + 0
    return math.sqrt(t)

def norm(v):
    t = 0
    for i in range(0, len(v)):
        try:
            t = t + math.pow(v[i],2)
        except OverflowError:
            t = t + 0
    return math.sqrt(t)
