import yarp
import time
from pyicub.api.iCubHelper import iCub, ROBOT_TYPE, ICUB_PARTS

yarp.Network.init()

def move(IPositionControl, IEncoders, target_joints, req_time):
    disp = [0]*len(target_joints)
    speed_head = [0]*len(target_joints)
    tmp = yarp.Vector(len(target_joints))

    encs=yarp.Vector(len(target_joints))
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

ipos_ctrl = icub.getIPositionControl(ICUB_PARTS.HEAD)
ienc = icub.getIEncoders(ICUB_PARTS.HEAD)
move(ipos_ctrl, ienc, [-15.0, 0.0, 0.0, 0.0, 0.0, 5.0], 1.0)
