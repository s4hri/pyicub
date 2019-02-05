import yarp
import time

class PositionController:

    def __init__(self, yarp_driver, joints_list):
        self.__IControlMode__ = yarp_driver.viewIControlMode()
        for joint in joints_list:
            self.__IControlMode__.setPositionMode(joint)
        self.__IPositionControl__ = yarp_driver.viewIPositionControl()

    def getIPositionControl(self):
        return self.__IPositionControl__

    def getIEncoders(self):
        return self.__IEncoders__
