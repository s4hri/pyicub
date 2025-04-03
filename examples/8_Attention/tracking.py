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

This script controls the iCub robot to visually track a point moving along a circular trajectory in 3D space.
It defines a dynamic visual target (a point on a circle) and commands the robot to follow it visually.

Usage:
------
python tracking.py
"""

# Import the helper interface for controlling the iCub robot
from pyicub.helper import iCub

# Import the VisualTarget module to define visual attention targets
from pyicub.modules.attention import VisualTarget

# Import math for trigonometric functions
import math

# Class to generate 3D points arranged in a circular trajectory
class CirclePoints:

    def __init__(self, radius, ratio, center=(0.0, 0.0, 0.0)):
        # Initialize with the radius of the circle, the ratio to define the number of points, and the center in 3D space
        self.radius = radius
        self.ratio = ratio
        self.center = center  # The center of the circle in 3D space (x, y, z)
        self.num_points = int(1 / ratio)  # Calculate the number of points based on the ratio
        self.current_index = 0  # To keep track of the current point index

    def _generate_points(self):
        # Infinite generator of points around the circle in 3D
        while True:
            # Calculate the angle for the current point
            angle = (2 * math.pi * self.current_index * self.ratio)  # Full circle (2pi) scaled by the ratio
            y = self.radius * math.cos(angle)  # Y coordinate on the perimeter of the circle
            z = self.radius * math.sin(angle)  # Z coordinate on the perimeter of the circle

            # The X-coordinate remains constant (as the circle is oriented in the YZ plane)
            x = self.center[0]  # Use the x value from the center

            # Adjust the coordinates based on the center offset
            y += self.center[1]
            z += self.center[2]

            # Update the index for the next point
            self.current_index = (self.current_index + 1) % self.num_points

            # Yield the current point as a 3D position
            yield (x, y, z)

    def get3DPosition(self):
        # Get the next point from the generator
        point_generator = self._generate_points()
        point = next(point_generator)  # Retrieve the next point from the generator

        return point

    def flush(self):
        # Placeholder for flush behavior if needed
        pass

# Main function that performs the tracking behavior
def tracking():
    # Initialize iCub interface
    icub = iCub()

    # Define the center of the circular trajectory in 3D space
    center = (-1.0, 0.0, 0.5)

    # Create a circle point generator with radius and sampling ratio
    circle = CirclePoints(radius=0.7, ratio=0.1, center=center)

    # Define a visual target with dynamic 3D position
    target = VisualTarget(
        name='pointOnACircle',
        callable_position=circle.get3DPosition,  # Function to get next point on circle
        callable_flush=circle.flush             # Optional flush method
    )

    # Register the visual target with the iCub attention system
    icub.attention.add_visual_target(target)

    # Start visual tracking of the moving target
    icub.attention.visual_tracking_scene(
        starting_point=center,
        target=target.name,
        fixation_time=0.5,           # Time to fixate on each point
        lookat_point_timeout=5.0,    # Timeout for looking at a point
        track_duration=10.0          # Total tracking duration
    )

# Execute tracking when script is run directly
if __name__ == "__main__":
    tracking()
