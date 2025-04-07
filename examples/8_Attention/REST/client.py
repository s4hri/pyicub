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

from pyicub.rest import PyiCubRESTfulClient

# Define the name of the robot and application as registered in the iCub server
robot_name = 'icubSim'
app_name = 'helper'

# Initialize the RESTful client to communicate with iCub on localhost and port 9001
client = PyiCubRESTfulClient(host='localhost', port=9001)

# Parameters for workspace observation (e.g., a table)
Table_center = (-1.0, 0.0, 0.0)       # 3D center of the workspace
Table_width = 0.6                     # Width of the workspace area
Table_depth = 0.4                     # Depth of the workspace area
num_points = 4                        # Number of fixation points
fixation_time = 1.0                  # Time in seconds to fixate on each point
lookat_point_timeout = 5.0           # Timeout in seconds for each lookat request

# Parameters for scene observation (area above the workspace)
Area_center = (-1.0, 0.0, 0.5)        # 3D center of the scene area
Area_width = 1.0                      # Width of the scene area
Area_height = 0.5                     # Height of the scene area

# Wait for user input to start the first request
input("PRESS ENTER to start the request")

# Send synchronous request to observe the workspace
client.run_target(
    robot_name=robot_name, 
    app_name=app_name, 
    target_name='attention.observe_workspace',
    center=Table_center, 
    width=Table_width, 
    depth=Table_depth, 
    num_points=num_points, 
    fixation_time=fixation_time, 
    lookat_point_timeout=lookat_point_timeout, 
    waitMotionDone=True               # Wait for the motion to complete before proceeding
)

# Wait for user input before starting the next observation
input("PRESS ENTER to start the request")

# Send asynchronous request to observe the scene (this won't block)
req_id = client.run_target_async(
    robot_name=robot_name, 
    app_name=app_name, 
    target_name='attention.observe_scene',
    center=Area_center, 
    width=Area_width, 
    height=Area_height, 
    num_points=num_points, 
    fixation_time=fixation_time, 
    lookat_point_timeout=lookat_point_timeout, 
    waitMotionDone=True              # Still ensures that the internal motion finishes
)

# Wait until the asynchronous request completes
print("WAITING FOR THE REQUEST TO FINISH...")
client.wait_until_completed(req_id)
