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
import sys
import time
import numpy as np
sys.path.append('../../')
from pyicub.api.iCubHelper import iCub, ROBOT_TYPE

yarp.Network.init()
icub = iCub(ROBOT_TYPE.ICUB)
ctrl = icub.getIGazeControl()

INIT_GAZE_POSITION = [-1.0, 0.0, 0.2]
GAZE_ANGLE_DISP = [-30.0, 0.0, 0.0]
GAZE_MAX_ANGLE_DISTRACTOR = [-70.0, 0.0, 0.0]

t0 = 0.0

def lookAt3DPoint(x, y, z):
    p = yarp.Vector(3)
    p.set(0, x)
    p.set(1, y)
    p.set(2, z)
    ctrl.lookAtFixationPointSync(p)

def lookAtRelAngle(azi,ele,ver, eyes_tt):
    p = yarp.Vector(3)
    p.set(0, azi)
    p.set(1, ele)
    p.set(2, ver)
    ctrl.lookAtRelAngles(p)
    time.sleep(eyes_tt)

def clearNeck():
    ctrl.clearNeckYaw()
    ctrl.clearNeckRoll()
    ctrl.clearNeckPitch()

def initParams(neck_tt=0.75, eyes_tt=0.25):
    clearNeck()
    ctrl.setNeckTrajTime(neck_tt)
    ctrl.setEyesTrajTime(eyes_tt)
    ctrl.clearEyes()

def blockNeck():
    ctrl.blockNeckYaw()
    ctrl.blockNeckRoll()
    ctrl.blockNeckPitch()

def TASK_INIT(neck_tt, eyes_tt):
    initParams(neck_tt, eyes_tt)
    lookAt3DPoint(INIT_GAZE_POSITION[0], INIT_GAZE_POSITION[1], INIT_GAZE_POSITION[2])
    time.sleep(2.0)
    blockNeck()
    lookAtRelAngle(GAZE_ANGLE_DISP[0]/2.0, GAZE_ANGLE_DISP[1]/2.0, GAZE_ANGLE_DISP[2]/2.0, 0.25)
    time.sleep(2.0)

def TASK_STEP1(step_duration, fixations_duration_low, fixations_duration_high, eyes_tt_low, eyes_tt_high):
    global t0
    t0 = time.time()
    print("0.0] TASK STEP 1 started")
    while True:
        fix_dur = np.random.uniform(fixations_duration_low, fixations_duration_high)
        gaze_position = [-GAZE_ANGLE_DISP[0], -GAZE_ANGLE_DISP[1], -GAZE_ANGLE_DISP[2]]
        eyes_tt = np.random.uniform(eyes_tt_low, eyes_tt_high)
        ctrl.setEyesTrajTime(eyes_tt)
        print("%.3f] Look at: %.2f %.2f %.2f Fixation duration: %.3f Eyes TT: %.3f" % (time.time() - t0, gaze_position[0], gaze_position[1], gaze_position[2], fix_dur, eyes_tt) )
        lookAtRelAngle(gaze_position[0], gaze_position[1], gaze_position[2], eyes_tt)
        time.sleep(fix_dur)
        if time.time() - t0 >= step_duration:
            break
        fix_dur = np.random.uniform(fixations_duration_low, fixations_duration_high)
        gaze_position = [GAZE_ANGLE_DISP[0], GAZE_ANGLE_DISP[1], GAZE_ANGLE_DISP[2]]
        eyes_tt = np.random.uniform(eyes_tt_low, eyes_tt_high)
        ctrl.setEyesTrajTime(eyes_tt)
        print("%.3f] Look at: %.2f %.2f %.2f Fixation duration: %.3f Eyes TT: %.3f" % (time.time() - t0, gaze_position[0], gaze_position[1], gaze_position[2], fix_dur, eyes_tt) )
        lookAtRelAngle(gaze_position[0], gaze_position[1], gaze_position[2], eyes_tt)
        time.sleep(fix_dur)
        if time.time() - t0 >= step_duration:
            break
    ctrl.stopControl()
    print("%.3f] TASK STEP 1 finished" % (time.time() - t0))

def TASK_STEP2(distractor_time):
    global t0
    lookAt3DPoint(INIT_GAZE_POSITION[0], INIT_GAZE_POSITION[1], INIT_GAZE_POSITION[2])
    ctrl.clearNeckYaw()
    time.sleep(10.0 - (time.time() - t0))
    print("%.3f] Looking at the distraction" % (time.time() - t0))
    lookAtRelAngle(GAZE_MAX_ANGLE_DISTRACTOR[0], GAZE_MAX_ANGLE_DISTRACTOR[1], GAZE_MAX_ANGLE_DISTRACTOR[2], 0.25)
    time.sleep(distractor_time)
    lookAt3DPoint(INIT_GAZE_POSITION[0], INIT_GAZE_POSITION[1], INIT_GAZE_POSITION[2])

raw_input("PRESS TO START INIT")
TASK_INIT(0.75, 0.25)
TASK_STEP1(step_duration=9.0, fixations_duration_low=0.4, fixations_duration_high=0.6, eyes_tt_low=0.1, eyes_tt_high=0.3)
TASK_STEP2(distractor_time=2.0)
