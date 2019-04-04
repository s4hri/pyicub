#   Copyright (C) 2019  Davide De Tommaso
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
import time

from pyicub.api.iCubHelper import iCub, ROBOT_TYPE, ICUB_PARTS

yarp.Network.init()

def move(IPositionControl, IEncoders, target_joints, req_time, joints_list):
    disp = [0]*len(joints_list)
    speed_head = [0]*len(joints_list)
    tmp = yarp.Vector(len(joints_list))
    encs=yarp.Vector(len(joints_list))
    encs=yarp.Vector(16)

    while not IEncoders.getEncoders(encs.data()):
        time.sleep(0.1)

    for i in range(0, len(target_joints)):
        tmp.set(i, target_joints[i])
        disp[i] = target_joints[i] - encs[i]
        if disp[i]<0.0:
            disp[i]=-disp[i]
        speed_head[i] = disp[i]/req_time
        IPositionControl.setRefSpeed(i, speed_head[i])
        IPositionControl.positionMove(i, tmp[i])

icub = iCub(ROBOT_TYPE.ICUB_SIMULATOR)
gaze_ctrl = icub.getIGazeControl()

torso_ctrl = icub.getIPositionControl(ICUB_PARTS.TORSO)
rightarm_ctrl = icub.getIPositionControl(ICUB_PARTS.RIGHT_ARM)
torso_ienc = icub.getIEncoders(ICUB_PARTS.TORSO)
rightarm_ienc = icub.getIEncoders(ICUB_PARTS.RIGHT_ARM)

p = yarp.Vector(3)
p.set(0, -0.4)
p.set(1, 0.0)
p.set(2, 0.1)
gaze_ctrl.setTrackingMode(True)
gaze_ctrl.lookAtFixationPoint(p)

#move(torso_ctrl, torso_ienc, [-39.0, 0.0, 0.0], 1.0)
move(rightarm_ctrl, rightarm_ienc, [10.06, 99.47, 5.31, 102.67, -13.50, -4.21],
                                    0.2,
                                    [0, 1, 2, 3, 4, 5])

t1 = time.time()
while not rightarm_ctrl.checkMotionDone():
    print rightarm_ctrl.checkMotionDone()
    time.sleep(0.2)
print time.time() - t1

raw_input()

#move(torso_ctrl, torso_ienc, [-24.0, 0.0, 0.0], 0.5)
move(rightarm_ctrl, rightarm_ienc, [9.97, 99.63, 6.34, 97.23, -10.95, -3.11],
                                    0.2,
                                    [0, 1, 2, 3, 4, 5])
t1 = time.time()
while not rightarm_ctrl.checkMotionDone():
    print rightarm_ctrl.checkMotionDone()
    time.sleep(0.2)
print time.time() - t1



"""
icub = iCub(ROBOT_TYPE.ICUB_SIMULATOR)

ctrl = icub.getPositionController(ICUB_PARTS.HEAD)
ctrl.move(joints=[-15.0, 0.0, 0.0, 0.0, 0.0, 5.0], req_time=1.0)

TORSO

1) -39.0 0.0 0.0
2) -24.0 0.0 0.0
3) -5.46 0.0 0.0
4) -4.63 0.0 0.0
5) -7.83 0.0 0.0
6) -11.0 0.0 0.0


RIGHT_ARM
1) 10.0650964122158 99.4687704013188 5.30701287581183 102.66576898523 -13.5035858756273 -4.21306729406253 39.6225027988811 50.0000000166639 30.0000000702435 17.9999999707381 86.000000042123 5.00000019112023 1.00000015207124 69.9999999863363 99.9999998965496 199.99999995111
2) 9.97017383828358 99.6302090414383 6.33941626892831 97.2294875635661 -10.9456953896816 -3.11179393981416 39.6288384594469 50.0000000060503 30.0000000659289 17.9999999667339 86.000000032274 5.00000019219974 1.0000001531926 69.9999999876438 99.999999894361 199.99999995823
3) -65.8691953695983 51.7502957732886 78.0918023889866 75.2739981259941 15.6202873594715 0.651750785457235 39.0348404117425 50.0000000060044 30.0000000653671 17.9999999624467 86.0000000378815 5.00000019259192 1.00000015329752 69.9999999976233 99.9999999036446 199.9999999678
4) -71.3216158426434 24.1811671315441 79.9873058906535 58.1013254964884 23.2869606336137 0.653950260411923 39.9987379760287 50.0000000066828 30.0000000653251 17.9999999603229 86.0000000393057 5.00000019276565 1.00000015347361 70.0000000013403 99.9999999061548 199.999999972327
5) -43.1304760157168 44.3272288889995 53.3197929882719 69.9668910602549 33.4804366010149 -0.000945383446099912 32.2646123503799 50.0000000053384 30.000000065371 17.9999999639938 86.0000000367118 5.00000019239846 1.00000015313491 69.999999994766 99.9999999016657 199.999999964095
6) -53.8199267375851 23.9168026421596 61.2631127945486 57.718352415598 40.2783729762949 0.62458389061504 39.7636682273287 50.0000000061674 30.0000000657533 17.9999999648164 86.0000000369473 5.00000019225762 1.0000001530241 69.9999999936402 99.9999999009518 199.999999962424
"""
