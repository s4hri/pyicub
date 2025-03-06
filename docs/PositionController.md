## Move_head.py

package used: pycub.helper. In theis package are used the classes iCub and JointPose and a constant called ICUB_HEAD.

So to move the  head just the classes iCub and JointPose are required, so let's see how the iCub class is defined.

Both the classes iCub and JointPosition are retrieved and defined by the file helper.py, so let's start commentin gthe file helper.py.


In the helper function, the pyicub package is used.

So basically the helper script seems to be an high level script that uses and combines the functionalities of the pyicub package.


HELPER.PY - classes:

1) iCubSingleton
2) iCub
3) PortMonitor



1) class iCubSingleton(**type**):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls.robot_name not in cls._instances.keys():
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls.robot_name] = instance
        return cls._instances[cls.robot_name]


**type**: indicates *inheritance* from the "type" metaclass, allowing it to control the creation and behavior of the classes that use it.

_istances: a class-level dictionary to store istances of classes using iCubSingleton. This ensures a single instance per *robot_name* (?)

call: overrides the __call__ method of the *type* masterclass, which is invoked when a class object is invoked like a function. (?)

cls: the class itself. Represent the class being instanciated.

*args,**kwargs: allows passing a variable number of positional and keyword arguments to the method.

cls.robot_name: Refers to the robot_name attribute of the class being instantiated.

cls._instances.keys(): Retrieves the keys (existing robot names) from the _instances dictionary. (?)

--
instance: A variable to hold the newly created object.

super(): Refers to the parent class (type), enabling calling the original __call__ method.

**.call(*args, kwargs): Invokes the original __call__ method of the parent type metaclass, creating the object.

return: Outputs the existing or newly created instance of the class.

cls._instances[cls.robot_name]: Retrieves the instance corresponding to the robot_name.

**Purpouse**: This class ensures the singleton pattern for any class that uses it as a metaclass. It restricts each robot_name to have exactly one instance so the purpouse is ensuring that only one istance of a class exist for a given robot_name.

(impedire che da una classe possa essere creato più di un oggetto,  Per farlo, l’oggetto desiderato viene creato all’interno di una classe per poi essere invocato come istanza statica.)

Creando un'istanza da una classe con il singleton design , ci si assicura che non ne venganon create delle altre. Il siungleton rende questa classe accessibile globalmente all'interno del software tramite uno dei metodi disponibili nei linguaggi di programmazione.


IN SHORT: using the metaclass iCubSingleton allows you to create a unique istance of a class given a robot_name without creating more than one istances for each robot_name. Than those istanciated classes are stored inside the attribute "_istances"

--------------

Now let's start with the iCub class:


# iCub Class Documentation

## Overview

The `iCub` class represents a high-level abstraction for interacting with the iCub robot. It provides mechanisms for managing the robot's parts, controllers, gaze, and actions. This class also facilitates interaction with the robot in both simulated and real-world environments. The class uses a singleton pattern to ensure only one instance exists.

---

## Class Definition

```python
class iCub(metaclass=iCubSingleton):
```

- **Superclass:** None
- **Metaclass:** `iCubSingleton`

The singleton pattern ensures only one instance of `iCub` is created during the application lifecycle.

---

## Constructor

### `__init__(self, robot_name="icub", request_manager=None, action_repository_path='', proxy_host=None)`

#### Parameters:

- **robot\_name** *(str)*: The name of the robot. Defaults to "icub".
- **request\_manager** *(iCubRequestsManager)*: Manages requests sent to the robot. Defaults to `None`.
- **action\_repository\_path** *(str)*: Path to the action repository (JSON files). Defaults to an empty string.
- **proxy\_host** *(str)*: Proxy host for camera or other connections. Defaults to `None`.

#### Key Actions:

1. Initializes various subsystems (position controllers, gaze controllers, services, etc.).
2. Loads actions from a repository if the path is provided.
3. Sets up simulation mode if the `ICUB_SIMULATION` environment variable is enabled.

---

## Attributes

### Internal Attributes:

- ***position\_controllers*** *(dict)*: Maps robot parts to their respective position controllers.
- ***services*** *(dict)*: Placeholder for service objects.
- ***gaze\_ctrl*** *(GazeController)*: Controller for managing the robot's gaze.
- ***emo*** *(EmotionsController)*: Controller for managing emotional expressions.
- ***speech*** *(iSpeakPyCtrl)*: Handles speech functionality.
- ***face*** *(FaceController)*: Manages facial expressions.
- ***facelandmarks*** *(FaceLandmarksController)*: Manages facial landmarks.
- ***cam\_right***, ***cam\_left*** *(CameraController)*: Manage left and right cameras.
- ***monitors*** *(list)*: Stores active port monitors.
- ***logger*** *(Logger)*: Used for logging messages.
- ***icub\_parts*** *(dict)*: Maps part names to their definitions.

---

## Public Methods

### Robot Initialization

#### `_initPositionControllers_()`

Initializes position controllers for all robot parts.

#### `_initGazeController_()`

Sets up the gaze controller.

### Action Management

#### `addAction(self, action, action_id=None)`

Adds an action to the repository.

#### `playAction(self, action_id, wait_for_completed=True, offset_ms=0.0)`

Executes a predefined action.

#### `importAction(self, JSON_file)`

Imports an action from a JSON file.

### Robot Interaction

#### `movePart(self, limb_motion, prefix='', ts_ref=0.0)`

Moves a specific robot part according to a `LimbMotion` object.

#### `moveGaze(self, gaze_motion, prefix='', ts_ref=0.0)`

Adjusts the robot's gaze based on a `GazeMotion` object.

### Miscellaneous

#### `close(self)`

Stops all monitors and closes YARP connections.

---

## Properties

### **logger**

Returns the logger instance.

### **gaze**

Returns the gaze controller, initializing it if not already set.

### **face**

Returns the face controller, initializing it if not already set.

### **cam\_right**, **cam\_left**

Return the respective camera controllers.

### **robot\_name**

Returns the robot's name.

---

## Usage Example

```python
from icub import iCub

# Create an iCub instance
robot = iCub(robot_name="icubSim", action_repository_path="/path/to/actions")

# Initialize gaze
robot.gaze.lookAt(1.0, 0.5, 0.3)

# Move a specific part
motion = LimbMotion(part=robot.parts["left_arm"], checkpoints=[...])
robot.movePart(motion)

# Play a predefined action
robot.playAction("wave_hand")

# Close the robot's connection
robot.close()
```

---

## Dependencies

- **YARP**: Required for communication with the robot.
- **Custom Controllers**: Includes `PositionController`, `GazeController`, and others for specific functionalities.

---

## Notes

- Ensure the `ICUB_SIMULATION` environment variable is set if using a simulated environment.
- The robot parts dictionary (`_icub_parts_`) must be populated with valid `iCubPart` instances before initializing controllers.




class PositionController


The PositionController class is designed to manage and control the movement of specific parts of the iCub robot using the YARP framework. Here’s a breakdown of its functionality:
Core Responsibilities

    Initialization and Setup
        The PositionController initializes the YARP RemoteControlboard to establish a connection to the specified robot part.
        It configures and retrieves necessary interfaces like encoders, control limits, control modes, and position control.

    Motion Control
        The class provides methods to set target positions and move the robot's joints to specified poses.
        Movements are controlled using speed, position, and time parameters, ensuring precision and adherence to constraints.

    Motion Monitoring
        It tracks whether the robot's part is currently moving or has completed its motion.
        The waitMotionDone method (and its variations) is used to wait until the motion is complete based on encoder readings, target positions, or elapsed time.

    Customizable Control
        The class supports setting custom motion completion criteria using setCustomWaitMotionDone, allowing flexibility in how the motion's end is detected.
        Users can override default behaviors by implementing alternative methods for waiting on motion completion.

    Logging
        Logs key information about motion events, including the start, completion, and timeout of movements, to assist in debugging and monitoring.

    Emergency Stops
        The stop method halts motion for the specified joints, ensuring safety during unexpected conditions.

    Control Mode Management2
        Ensures the robot's control mode is set to position control mode before initiating movement.

Key Methods

    move(pose, req_time, timeout, joints_speed, waitMotionDone, tag)
        Executes the movement of joints based on a specified pose and other parameters. Supports optional waiting for the motion to complete.

    waitMotionDone(req_time, timeout)
        Monitors the motion and returns True if it completes within the specified timeout, otherwise returns False.

    setPositionControlMode(joints_list)
        Configures the control mode of the robot's joints to position control for precise movements.

    stop(joints_list)
        Stops all or specified joints immediately by setting their reference speed to zero.

How It Works

The class uses YARP's interfaces to:

    Get the current position of the joints using encoders.
    Set target positions and speeds for the joints.
    Move the joints by sending position commands to the control board.
    Monitor and wait until the motion is complete, using one of the customizable motion completion criteria.

Intended Use

This class is essential for controlling and coordinating the movements of specific parts of the iCub robot, such as its arms, head, or legs, in tasks requiring precision and controlled motion. It abstracts the complexities of directly interfacing with YARP and provides a higher-level interface for developers.


