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


"""
tracking.py
============

This script ...

Usage:
------
...

"""

from pyicub.helper import iCub
from pyicub.modules.attention import VisualTarget

import math

import math

class CirclePoints:

    def __init__(self, radius, ratio, center=(0.0, 0.0, 0.0)):
        # Initialize with the radius of the circle, the ratio to define the number of points, and the center in 3D space
        self.radius = radius
        self.ratio = ratio
        self.center = center  # The center of the circle in 3D space (x, y, z)
        self.num_points = int(1 / ratio)  # Calculate the number of points based on the ratio
        self.current_index = 0  # To keep track of the current point

    def _generate_points(self):
        # Infinite generator of points around the circle in 3D
        while True:
            # Calculate the angle for the current point
            angle = (2 * math.pi * self.current_index * self.ratio)  # Full circle (2pi) scaled by the ratio
            y = self.radius * math.cos(angle)  # X coordinate on the perimeter
            z = self.radius * math.sin(angle)  # Y coordinate on the perimeter
            
            # The Z-coordinate remains constant
            x = self.center[0]  # Use the z value from the center

            # Adjust the coordinates based on the center
            y += self.center[1]
            z += self.center[2]
            
            # Update the index for the next point
            self.current_index = (self.current_index + 1) % self.num_points
            
            yield (x, y, z)  # Yield the current point as a 3D point
    
    def get3DPosition(self):
        # Get the next point from the generator
        point_generator = self._generate_points()
        point = next(point_generator)  # Get the next point
        
        return point

    def flush(self):
        pass

def tracking():
    icub = iCub()

    center = (-1.0, 0.0, 0.5)
    circle = CirclePoints(radius=0.7, ratio=0.1, center=center)
    target = VisualTarget(name='pointOnACircle', callable_position=circle.get3DPosition, callable_flush=circle.flush)

    icub.attention.add_visual_target(target)
    
    icub.attention.visual_tracking_scene(starting_point=center, target=target.name, fixation_time=0.5, lookat_point_timeout=5.0, track_duration=10.0)

if __name__ == "__main__":
    tracking()

