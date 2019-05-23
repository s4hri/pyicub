# pyicub
Yarp interface for using the iCub robot with Python

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


