import yarp
import sys
sys.path.append('../../')
from pyicub.api.iCubHelper import iCub, ROBOT_TYPE

yarp.Network.init()
#yarp.Network.setLocalMode(True)

icub = iCub(ROBOT_TYPE.ICUB)
ctrl = icub.getIGazeControl()

p = yarp.Vector(3)
p.set(0, -1.0)
p.set(1, 0.2)
p.set(2, -0.4)

ctrl.lookAtFixationPoint(p)

"""
options = yarp.Property()
driver = yarp.PolyDriver()

# set the poly driver options
options.put("device", "gazecontrollerclient")
options.put("local", "/gaze_client")
options.put("remote", "/iKinGazeCtrl")

# opening the drivers
print 'Opening the motor driver...'
driver.open(options)
if not driver.isValid():
    print 'Cannot open the driver!'
    sys.exit()
"""
