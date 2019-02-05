import yarp
from pyicub.api.yarp_classes.GazeController import GazeController
from pyicub.api.yarp_classes.PositionController import PositionController
from pyicub.api.yarp_modules.emotions import emotionsPyCtrl
from pyicub.api.yarp_modules.speech import speechPyCtrl

class iCubPart:
    def __init__(self, name, joints_n):
        self.name = name
        self.joints_n = joints_n

class ROBOT_TYPE:
    ICUB = "icub"
    ICUB_SIMULATOR = "icubSim"

class ICUB_PARTS:
    HEAD = iCubPart("head", 6)
    LEFT_ARM = iCubPart("left_arm", 16)
    RIGHT_ARM = iCubPart("right_arm", 16)
    TORSO = iCubPart("torso", 3)
    LEFT_LEG = iCubPart("left_leg", 6)
    RIGHT_LEG = iCubPart("right_leg", 6)

class iCub:
    def __init__(self, robot):
        self.__robot__ = robot
        self.__gaze_controller__ = None
        self.__emotions_mod__ = None
        self.__speech_mod__ = None
        self.__position_controllers__ = {}
        self.__drivers__ = {}
        self.__encoders__ = {}

    def getEmotionsModule(self):
        if self.__emotions_mod__ is None:
            self.__emotions_mod__ = emotionsPyCtrl()
        return self.__emotions_mod__

    def getIGazeControl(self):
        if self.__gaze_controller__ is None:
            self.__gaze_controller__ = GazeController()
        return self.__gaze_controller__.getIGazeControl()

    def getRobotPartProperties(self, robot_part):
        props = yarp.Property()
        props.put("device","remote_controlboard")
        props.put("local","/client/" + robot_part.name)
        props.put("remote","/" + self.__robot__ + "/" + robot_part.name)
        return props

    def getDriver(self, robot_part):
        if not robot_part.name in self.__drivers__.keys():
            props = self.getRobotPartProperties(robot_part)
            self.__drivers__[robot_part.name] = yarp.PolyDriver(props)
        return self.__drivers__[robot_part.name]

    def getIPositionControl(self, robot_part, joints_list=None):
        if not robot_part.name in self.__position_controllers__.keys():
            driver = self.getDriver(robot_part)
            if joints_list is None:
                joints_list = range(0, robot_part.joints_n)
            self.__position_controllers__[robot_part.name] = PositionController(driver, joints_list)
        return self.__position_controllers__[robot_part.name].getIPositionControl()

    def getIEncoders(self, robot_part, driver=None):
        if not robot_part.name in self.__encoders__.keys():
            driver = self.getDriver(robot_part)
            self.__encoders__[robot_part.name] = driver.viewIEncoders()
        return self.__encoders__[robot_part.name]

    def say(self, message):
        if self.__speech_mod__ is None:
            self.__speech_mod__ = speechPyCtrl()
        self.__speech_mod__.say(message)
