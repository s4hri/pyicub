# pyicub
Python library using YARP wrappers for developing iCub applications


# Requirements

Python >3.5
Yarp >3 (and Python wrappers availables in the PYTHONPATH)

# installation

## Ubuntu with checkinstall

On Ubuntu systems just do:
```
sudo make install
```
it requires checkinstall:
```
sudo apt install checkinstall
```

## Any linux, easy_install

If not on Ubuntu you can use easy_install:
```
python setup.py install
```
or
```
python3 setup.py install
```
depending on which one of those is linked to the yarp Python bindings.

Remember, to uninstall just remove the directory /usr/lib64/python3.7/site-packages/pyicub-whatever.egg
and the entry from /usr/lib64/python3.7/site-packages/easy-install.pth.

# Any linux, pip

Just type
```
pip install .
```
or
```
pip3 install .
```

# Usage example

```
import yarp
yarp.Network.init()

from pyicub import *
icub = iCub( ROBOT_TYPE.ICUB_SIMULATOR )
rightarm = icub.getPositionController( ICUB_PARTS.RIGHT_ARM )
rightarm.move(  target_joints=[10.06, 99.47, 5.31, 102.67, -13.50, -4.21], \
                req_time=1.0, joints_list=[0,1,2,3,4,5], waitMotionDone=True )
rightarm.move( target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], \
                req_time=1.0, joints_list=[0,1,2,3,4,5], waitMotionDone=True )

```


## Usage in Matlab

Just after starting the Matlab be sure to choose the version of python that actually has yarp bindings,
for example: (you can check the current one using py.sys.path)
```matlab
pyversion('/usr/bin/python3')
```
and an example showing how to move the head
```matlab
py.time.time() % just to be sure that the Python engine started...

py.yarp.Network.init()
icub = py.pyicub.iCub( 'icubSim' )

head_ctrl = icub.getPositionController(py.pyicub.iCubPart("head",int32(6)))
while(1)
    head_ctrl.move(py.list({-15.0, 0.0, 0.0, 0.0, 0.0, 5.0}), 1.2)
    pause(1)
    head_ctrl.move(py.list({-1.0, 0.0, 0.0, 0.0, 0.0, 5.0}), 1.2)
    pause(1)
end
```
and moving the arm up and down
```matlab
py.time.time()
py.yarp.Network.init()
icub = py.pyicub.iCub( 'icubSim' )

rightarm = icub.getPositionController( py.pyicub.iCubPart("right_arm", int32(16)) )

while(1)
    rightarm.move(py.list({0.1, 0.1, 0.1, 0.1, 0.1, 0.1,0,0,0,0,0,0,0,0,0,0}),1.1)
    pause(1)
    rightarm.move(py.list({10.06, 99.47, 5.31, 102.67, -13.50, -4.21,0,0,0,0,0,0,0,0,0,0}),1.1)
    pause(1)
end
```

General notes:
- storing py.list() as a matlab variable sometimes breaks everything
- int32() is required when values are expected to be int in python
