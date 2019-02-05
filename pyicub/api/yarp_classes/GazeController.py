import yarp
import sys

class GazeController:

    def __init__(self):
        self.__props__ = yarp.Property()
        self.__driver__ = yarp.PolyDriver()
        self.__props__.put("robot", "icub")
        self.__props__.put("device","gazecontrollerclient")
        self.__props__.put("local","/gaze_client")
        self.__props__.put("remote","/iKinGazeCtrl")

        self.__driver__.open(self.__props__)
        if not self.__driver__.isValid():
            print 'Cannot open GazeController driver!'
            sys.exit()
        self.__IGazeControl__ = self.__driver__.viewIGazeControl()

    def getIGazeControl(self):
        return self.__IGazeControl__

    def __del__(self):
        self.__driver__.close()
