import yarp
from pyicub.core.logger import YarpLogger
from pyicub.controllers.position import PositionController
from pyicub.helper import iCub

import xml.etree.cElementTree as ET
from xml.dom import minidom
import os
import sys
from threading import Thread
from concurrent.futures.thread import ThreadPoolExecutor

class RFM_Plotter(yarp.RFModule):

    def __init__(self, robot_name, robot_part, positionController: PositionController):
        self._logger_ = YarpLogger.getLogger()
        self._logger_.debug("Initializing plotter module <%s> ..." % robot_part)
        #
        yarp.RFModule.__init__(self)
        #
        self._period_ = 0.01
        # define ports
        self._rpc_module_ = yarp.Port()
        self._port_pos_   = yarp.BufferedPortVector()
        self._port_vel_   = yarp.BufferedPortVector()
        self._port_acc_   = yarp.BufferedPortVector()
        self._port_r_pos_ = yarp.BufferedPortVector()
        self._port_r_vel_ = yarp.BufferedPortVector()
        self._port_r_acc_ = yarp.BufferedPortVector()
        #
        self._posCtrl_   = positionController
        self._iPos_      = positionController.getIPositionControl()
        self._iEnc_      = positionController.getIEncoders()
        self._iCtrlLim_  = positionController.getIControlLimits()
        #
        self._robot_     = robot_name
        self._part_      = robot_part
        #
        self._remote_    = "/%s/%s" % (robot_name, robot_part)
        #
        self._scope_     = None
        self._closing_   = False
        self.OUTPUT_DIR  = "/tmp/scope/"
        self._file_name_ = self.OUTPUT_DIR + self._posCtrl_.__part_name__ + ".xml"

    def configure(self, rf, robot_name):
        self._logger_.debug("Configure module ...")
        # check - resource finder
        #
        self._joints_ = self._iEnc_.getAxes()
        #
        self._pos_   = yarp.Vector(self._joints_)
        self._vel_   = yarp.Vector(self._joints_)
        self._acc_   = yarp.Vector(self._joints_)
        self._r_pos_ = yarp.Vector(self._joints_)
        self._r_vel_ = yarp.Vector(self._joints_)
        self._r_acc_ = yarp.Vector(self._joints_)
        #
        self._rpc_module_.open(self._remote_ + "/plotter:rpc")
        self.attach(self._rpc_module_)
        #
        self._port_pos_.open(self._remote_ + "/pos:o")
        self._port_vel_.open(self._remote_ + "/vel:o")
        self._port_acc_.open(self._remote_ + "/acc:o")
        self._port_r_pos_.open(self._remote_ + "/ref_pos:o")
        self._port_r_vel_.open(self._remote_ + "/ref_vel:o")
        self._port_r_acc_.open(self._remote_ + "/ref_acc:o")

        self.getScopeXMLFilename(robot_name)

        return True


    def getPeriod(self):
        return self._period_


    def updateModule(self):
        # get pos/vel/acc
        self._iEnc_.getEncoders(self._pos_.data())
        self._iEnc_.getEncoderSpeeds(self._vel_.data())
        self._iEnc_.getEncoderAccelerations(self._acc_.data())
        # get ref pos/vel/acc
        self._iPos_.getTargetPositions(self._r_pos_.data())
        self._iPos_.getRefSpeeds(self._r_vel_.data())
        self._iPos_.getRefAccelerations(self._r_acc_.data())
        self.writePortVector()

        return not self._closing_


    def writePortVector(self):
        # prepare bottle pos/vel/acc
        self._bot_pos_   = self._port_pos_.prepare()
        self._bot_vel_   = self._port_vel_.prepare()
        self._bot_acc_   = self._port_acc_.prepare()
        # prepare bottle ref pos/vel/acc
        self._bot_r_pos_ = self._port_r_pos_.prepare()
        self._bot_r_vel_ = self._port_r_vel_.prepare()
        self._bot_r_acc_ = self._port_r_acc_.prepare()
        #
        self._bot_pos_.clear()
        self._bot_vel_.clear()
        self._bot_acc_.clear()
        self._bot_r_pos_.clear()
        self._bot_r_vel_.clear()
        self._bot_r_acc_.clear()
        #
        for i in range(self._joints_):
            # add pos/ref/acc
            self._bot_pos_.push_back(self._pos_[i])
            self._bot_vel_.push_back(self._vel_[i])
            self._bot_acc_.push_back(self._acc_[i])
            # add pos/ref/acc
            self._bot_r_pos_.push_back(self._r_pos_[i])
            self._bot_r_vel_.push_back(self._r_vel_[i])
            self._bot_r_acc_.push_back(self._r_acc_[i])
        # write pos/vel/acc
        self._port_pos_.write()
        self._port_vel_.write()
        self._port_acc_.write()
        # write pos/vel/acc
        self._port_r_pos_.write()
        self._port_r_vel_.write()
        self._port_r_acc_.write()

        return True


    def getScopeXMLFilename(self, robot_name):
        self._logger_ = YarpLogger.getLogger()
        self._logger_.debug("generating ScopeXml ...")

        if not os.path.exists(self.OUTPUT_DIR):
            self._logger_.debug("Create directory %s ..." % (self.OUTPUT_DIR))
            os.mkdir(self.OUTPUT_DIR)

        joints = self._iEnc_.getAxes()
        if joints == 3:
            _rows    = 1
            _columns = 3
        elif joints == 6:
            _rows    = 2
            _columns = 3
        elif joints == 16:
            _rows    = 4
            _columns = 4

        portscope = ET.Element("portscope", rows = str(_rows), columns = str(_columns))

        index = 0
        for i in range(_rows):
            for j in range(_columns):
                min_p = yarp.Vector(1)
                max_p = yarp.Vector(1)
                self._iCtrlLim_.getLimits(index, min_p.data(), max_p.data())
                _min = min_p[0] - 10
                _max = max_p[0] + 10
                plot = ET.SubElement(portscope, "plot", gridx=str(j), gridy=str(i), hspan="1", vspan="1", title="Joint %s" % (index), minval=str(_min), maxval=str(_max), bgcolor="LightSlateGrey")
                ET.SubElement(plot, "graph", remote="/" + robot_name + "/" + self._posCtrl_.__part_name__ + "/pos:o"    , index = str(index), color="Blue"  , size="3", type="lines")
                ET.SubElement(plot, "graph", remote="/" + robot_name + "/" + self._posCtrl_.__part_name__ + "/vel:o"    , index = str(index), color="Red"   , size="1", type="lines")
                ET.SubElement(plot, "graph", remote="/" + robot_name + "/" + self._posCtrl_.__part_name__ + "/acc:o"    , index = str(index), color="Orange", size="1", type="lines")
                ET.SubElement(plot, "graph", remote="/" + robot_name + "/" + self._posCtrl_.__part_name__ + "/ref_pos:o", index = str(index), color="Green" , size="3", type="lines")
                index += 1

        tree = minidom.parseString(ET.tostring(portscope)).toprettyxml(indent='\t')
        with open(self._file_name_, 'w') as f:
            f.write(tree)

        return True


    def respond(self, command, reply):
        if command.check("period"):
            self._period_ = command.find("period").asFloat64()
            reply.addString("ack")
            return True

        return True


    def interruptModule(self):
        self._logger_.debug("Interrupting module %s ... " % (self._part_))
        #
        self._rpc_module_.interrupt()
        #
        self._port_pos_.interrupt()
        self._port_vel_.interrupt()
        self._port_acc_.interrupt()
        #
        self._port_r_pos_.interrupt()
        self._port_r_vel_.interrupt()
        self._port_r_acc_.interrupt()
        #
        return True


    def close(self):
        self._logger_.debug("Closing module %s ... " % (self._part_))
        #
        self._rpc_module_.close()
        #
        self._port_pos_.close()
        self._port_vel_.close()
        self._port_acc_.close()
        #
        self._port_r_pos_.close()
        self._port_r_vel_.close()
        self._port_r_acc_.close()

        self._closing_ = True
        return True



def plotter_scope(plotter):
    t = Thread(target=plotter.runModule)
    t.start()
    os.system("yarpscope --xml %s --title %s" % (plotter._file_name_, plotter._file_name_))
    plotter.close()
    t.join()


if __name__ == '__main__':

    log = YarpLogger.getLogger()

    yarp.Network.init()
    icub = iCub()
    plotters = []

    if not sys.argv[1:]:
        log.error("!! NO ARGS !! - please provide parts to monitoring (ex: <head> <right_arm> <torso> ... )")
        exit()

    for part in sys.argv[1:]:
        if part in icub.parts.keys():
            positionCtrl = icub.getPositionController(part)
            if positionCtrl:
                plotter = RFM_Plotter(icub.robot_name, part, positionCtrl)
                plotter.configure(None, icub.robot_name)
                plotters.append(plotter)

    with ThreadPoolExecutor(max_workers=10) as executor:
        for plotter in plotters:
            executor.submit(plotter_scope, plotter)
