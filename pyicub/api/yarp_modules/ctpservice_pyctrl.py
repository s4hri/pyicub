# ctpservice_pyctrl.py

import yarp
import time
import numpy
from scipy.linalg import norm
from threading import Thread
from threading import Event
from rpc_pyctrl import rpcMod
from port_pyctrl import yarpReadPortPyCtrl


class ctpServicePyCtrl:

    def __init__(self, robot_part, simulation = False, logging_trajectory = False):
        self._rpcMod = rpcMod("/ctpServicePyCtrl_%s" % robot_part, "/ctpservice/%s/rpc" % robot_part)
        self._robot = "icubSim" if simulation else "icub"
        self._robot_part = robot_part
        self._joint_state_port = yarpReadPortPyCtrl("/%s/%s/state:o" % (self._robot, robot_part), "/ctpServicePyCtrl/%s/state:i" % robot_part)
        self._joint_stateExt_port = yarpReadPortPyCtrl("/%s/%s/stateExt:o" % (self._robot, robot_part), "/ctpServicePyCtrl/%s/stateExt:i" % robot_part)
        self._ongoing_start_ts = None
        self._ongoing_end_ts = None
        self._onset_vel = 0.0
        if logging_trajectory:
            self._logging_trajectory = True
        else:
            self._logging_trajectory = False


    def _waitForMotionOnset(self):
        while True:
            vel = self.getJointsNormVel()
            if vel > 0.1:
                return vel
            time.sleep(0.01)

    def _waitForMotionOffset(self):
        while True:
            vel = self.getJointsNormVel()
            if vel < 1.0:
                return vel
            time.sleep(0.01)



    def sendJPos(self, req_time, req_offset, req_joints, wait_to_complete = True):
        cmd = yarp.Bottle()
        cmd.clear()
        map(cmd.addString, ["ctpq", "time"])
        map(cmd.addDouble, [req_time])
        map(cmd.addString, ["off"])
        map(cmd.addDouble, [req_offset])
        map(cmd.addString, ["pos"])
        joints = cmd.addList()
        map(joints.addDouble, req_joints)
        if self.getJointsStateErrFrom(req_joints) > 5.0:
            self._rpcMod.execute(cmd)
            if wait_to_complete:
                self._wait_until_motion_is_complete(req_time)
            else:
                self._ongoing_start_ts = self._ongoing_end_ts = time.time()
        else:
            self._ongoing_start_ts = self._ongoing_end_ts = time.time()

        return [self.getJointsStateErrFrom(req_joints), self.getOnsetVel(), self.getJointsVel(), self.getOngoingStartTs(), self.getOngoingEndTs(), self.getTrajectoryTime()]


    def getOngoingStartTs(self):
        return self._ongoing_start_ts

    def getOngoingEndTs(self):
        return self._ongoing_end_ts

    def getOnsetVel(self):
        return self._onset_vel

    def getTrajectoryTime(self):
        return (self._ongoing_end_ts - self._ongoing_start_ts)

    def getJointsTrajectory(self):
        return self._joints_trajectory

    def _wait_until_motion_is_complete(self, req_time):
        self._onset_vel = self._waitForMotionOnset()
        self._ongoing_start_ts = time.time()

        if self._logging_trajectory:
            self._joints_trajectory = []
            for i in range(0,11):
                btl = self._joint_state_port.read()
                self._joints_trajectory.append(map(float, btl.toString().split(" ")))
                time.sleep(req_time/10)
        else:
            time.sleep(req_time)

        self._waitForMotionOffset()
        self._ongoing_end_ts = time.time()

    def getJointsStateErrFrom(self, target_joint_state):
        current_joint_state = []

        btl = self._joint_state_port.read()
        if btl:
            for i in range(0, btl.size()):
                current_joint_state.insert(i, btl.get(i).asDouble())
            if len(current_joint_state) == len(target_joint_state):
                return norm(numpy.diff(numpy.array([current_joint_state,target_joint_state]), axis=0))
        return None

    def getJointsVel(self):
        btl = self._joint_stateExt_port.read()
        return map(float, btl.get(2).toString().split(" "))


    def getJointsNormVel(self):
        vel = self.getJointsVel()[0:6]
        return numpy.linalg.norm(numpy.array([vel]))

    def close(self):
        self._joint_state_port.close()
        self._joint_stateExt_port.close()
        self._rpcMod.close()
