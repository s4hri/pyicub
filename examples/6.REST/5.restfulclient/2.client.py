# BSD 2-Clause License
#
# Copyright (c) 2022, Social Cognition in Human-Robot Interaction,
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

client = PyiCubRESTfulClient(host='localhost', port=9001)

print("PyiCub ver: ", client.get_version())

robots = client.get_robots()

print("Robots: ")
for robot in robots:
    print("name: '%s' url: '%s'" % (robot.name, robot.url))

    applications = client.get_apps(robot.name)
    
    print("\t Robot Apps: ")
    for app in applications:
        print("\t -> name: '%s' url: '%s'" % (app.name, app.url))

        services = client.get_services(robot.name, app.name)
        
        print("\t\t Applications Services: ")
        for service in services.values():
            print("\t\t name: '%s' url: '%s'" % (service.name, service.url))

    actions = client.get_robot_actions(robot.name)
    print("\t Robot Actions: ")
    for action_id in actions:
        print("\t -> action_id: %s" % action_id)
        client.play_action(robot.name, action_id=action_id)
