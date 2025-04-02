# BSD 2-Clause License
#
# Copyright (c) 2025, Social Cognition in Human-Robot Interaction,
#                     Istituto Italiano di Tecnologia, Genova
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from pyicub.controllers.gaze import GazeController

import numpy as np
import time
import logging
import yarp
import random
import threading

yarp.Network().init()

logger = logging.getLogger("VisualAttention")
logger.setLevel(logging.INFO)

class VisualTarget:

    def __init__(self, name, callable_position, callable_flush):
        self.name = name
        self.callable_position = callable_position
        self.callable_flush = callable_flush
    
    def get_position(self):
        res = self.callable_position()
        if res:
            return res
        else:
            return None
        
    def flush(self):
        self.callable_flush()

class VisualAttention():
    AZI_MIN = -30
    AZI_MAX = 30
    ELE_MIN = -25
    ELE_MAX = 20
    VER_MIN = 0
    VER_MAX = 10

    def __init__(self, gazectrl):
        self.__visual_targets__ = {}
        self.tracking_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.gazectrl = gazectrl

    def __checkRange__(self, angles):
        """
        Check if the azimuth, elevation and vergence angles are within the allowed range.
        
        Parameters:
        - angles (tuple): A tuple (azimuth, elevation, vergence) in degrees.
        
        Returns:
        - bool: True if the angles are within the safe range, False otherwise.
        """
        azimuth, elevation, vergence = angles
        return (self.AZI_MIN < azimuth < self.AZI_MAX) and (self.ELE_MIN < elevation < self.ELE_MAX) and (self.VER_MIN < vergence < self.VER_MAX)

    
    def __is_safe__(self, P):
        p = yarp.Vector(3)
        p.set(0, P[0])
        p.set(1, P[1])
        p.set(2, P[2])
        angles = yarp.Vector(3)
        self.gazectrl.IGazeControl.getAnglesFrom3DPoint(p, angles)
        res = self.__checkRange__((angles.get(0), angles.get(1), angles.get(2)))
        if not res:
            logger.warning('Head angles not safe: %.2f %.2f %.2f' % (angles.get(0), angles.get(1), angles.get(2)))
        return res
  
    @property
    def targets(self):
        return self.__visual_targets__

    def add_visual_target(self, name, callable_position, callable_flush):
        self.__visual_targets__[name] = VisualTarget(name, callable_position, callable_flush)

    def grid_ellipsoid(self, P, a, b, c, num_points):
        """
        Generate well-distributed points on the surface of an ellipsoid, balancing the variation on x, y, and z 
        according to the proportions of the ellipsoid's semi-major axes.

        Parameters:
        - P (tuple): The center of the ellipsoid (x, y, z).
        - a, b, c (float): The semi-major axes of the ellipsoid along the x, y, and z directions.
        - num_points (int): The number of points to generate on the surface.

        Returns:
        - List of tuples representing points on the surface of the ellipsoid.
        """
        points = []

        # Use proportional latitude and longitude steps to balance the distribution
        lat_steps = int(np.sqrt(num_points))  # Number of steps for latitude
        lon_steps = num_points // lat_steps   # Number of steps for longitude

        # Latitude: Varies between -pi/4 and pi/4, balanced by the ratio of the z-axis (c)
        latitudes = np.linspace(-np.pi / 4, np.pi / 4, lat_steps)

        # Longitude: Full span along the y-axis, balanced by the ratio of the y-axis (b)
        longitudes = np.linspace(-np.pi / 2, np.pi / 2, lon_steps)

        for lat in latitudes:
            for lon in longitudes:
                # Use parametric equation for ellipsoid with proportional scaling for each axis
                x = a * np.cos(lat)  # Depth variation, scaled by `a`
                y = b * np.sin(lon)  # Left-right variation, scaled by `b`
                z = c * np.sin(lat)  # Height variation, scaled by `c`

                # Translate the point by the center P
                point = (P[0] + x, P[1] + y, P[2] + z)
                points.append(point)

        # Shuffle the points randomly to vary the observation order
        random.shuffle(points)

        # Ensure the list contains exactly num_points points
        return points[:num_points]

    def hello_world(self, name: str='you'):
        return "Hello world %s!" % name
    
    def observe_area(self, P, a, b, c, num_points=10, fixation_time=2.0, lookat_point_timeout=5.0, waitMotionDone=True):
        """
        Random observation of points within a 3D ellipse centered at P.

        Parameters:
        - P (tuple): The center of the ellipse (x, y, z).
        - a (float): Semi-major axis length along the x-axis.
        - b (float): Semi-major axis length along the y-axis.
        - c (float): Semi-major axis length along the z-axis.
        - num_points (int, optional): The number of points to observe. Default is 10.
        """
        logger.info('Observing Area - START - Center: %s, Axes: (%.2f, %.2f, %.2f), Num Points: %d, Fixation Time: %.2f' % (P, a, b, c, num_points, fixation_time))

        points = self.grid_ellipsoid(P, a, b, c, num_points)
            
        res = self.observe_points(points, fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout, waitMotionDone=waitMotionDone)

        logger.info('Observing Area - END')
        
        return res

    def observe_workspace(self, center, width, depth, num_points=10, fixation_time=2.0, lookat_point_timeout=5.0, waitMotionDone=True):
        """
        Observes random, well-distributed points within a desk-like workspace.
        
        Parameters:
        - center (tuple): The center of the workspace (x, y, z).
        - width (float): The width of the workspace along the y-axis.
        - depth (float): The depth of the workspace along the x-axis.
        - num_points (int, optional): The number of points to observe. Default is 10.
        - fixation_time (float, optional): Time in seconds the robot should observe each point. Default is 2.0 seconds.
        - lookat_point_timeout (float, optional): Timeout for each point. Default is 5.0 seconds.
        """

        logger.info('Observing Workspace - START - Center: %s, Width: %.2f, Depth: %.2f, Num Points: %d, Fixation Time: %.2f' % 
                    (center, width, depth, num_points, fixation_time))

        # Proportional scaling of the axes
        height = 0.1  # Set a small fixed height, since the workspace is mostly flat

        # Generate well-distributed points within the workspace using the balanced grid ellipsoid method
        points = self.grid_ellipsoid(center, depth / 2, width / 2, height / 2, num_points)

        res = self.observe_points(points, fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout, waitMotionDone=waitMotionDone)

        logger.info('Observing Workspace - END')

        return res

    def observe_scene(self, center, width, height, num_points=10, fixation_time=2.0, lookat_point_timeout=5.0, waitMotionDone=True):
        """
        Observes well-distributed points within a scene in front of the robot.
        
        Parameters:
        - center (tuple): The center of the scene in front of the robot (x, y, z).
        - width (float): The width of the scene along the y-axis.
        - height (float): The height of the scene along the z-axis.
        - num_points (int, optional): The number of points to observe. Default is 10.
        - fixation_time (float, optional): Time in seconds the robot should observe each point. Default is 2.0 seconds.
        - lookat_point_timeout (float, optional): Timeout for each point. Default is 5.0 seconds.
        """

        logger.info('Observing Scene - START - Center: %s, Width: %.2f, Height: %.2f, Num Points: %d, Fixation Time: %.2f' % 
                    (center, width, height, num_points, fixation_time))

        # Proportional scaling of the axes for the scene in front of the robot
        depth = 0.1  # Small fixed depth, since the scene is directly in front of the robot

        # Generate well-distributed points within the scene using the grid ellipsoid method
        points = self.grid_ellipsoid(center, depth / 2, width / 2, height / 2, num_points)

        # Instruct the robot to observe the generated points
        res = self.observe_points(points, fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout, waitMotionDone=waitMotionDone)

        logger.info('Observing Scene - END')

        return res


    def observe_points(self, points_list, fixation_time=2.0, lookat_point_timeout=5.0, waitMotionDone=True):
        """
        Sequenced observation of a list of predefined 3D points with a specified fixation time.

        Parameters:
        - points_list (list of tuples): A list of 3D points to observe (each point is a tuple (x, y, z)).
        - fixation_time (float, optional): The time in seconds the robot should observe each point. Default is 1.0 seconds.
        """
        logger.info('Observing Points - START - Num Points: %d, Fixation Time: %.2f' % (len(points_list), fixation_time))

        detected_targets = {}

        for point in points_list:
            if not point:
                logger.warning('Invalid point detected. Skipping...')
                continue
            # Observe the point only if is in the safe range
            if self.__is_safe__(point):
                logger.debug('Looking at point %.2f %.2f %.2f' % (point[0], point[1], point[2]))
                self.gazectrl.lookAtFixationPoint(point[0], point[1], point[2], waitMotionDone=waitMotionDone, timeout=lookat_point_timeout)
                time.sleep(fixation_time)

                # Checking for targets
                if self.targets:
                    for k, v in self.targets.items():
                        target_pos = self.targets[k].get_position()
                        if target_pos:
                            if not k in detected_targets.keys():
                                detected_targets[k] = []
                            detected_targets[k].append(target_pos)
            else:
                logger.warning('Point %s is out of the safe range. Skipping...' % str(point))

        logger.info('Observing Points - END')

        return detected_targets

    def track_moving_point(self, target, track_duration=10.0, fixation_time=2.0, lookat_point_timeout=5.0, waitMotionDone=False):
        """
        Track a moving point over a specified duration, updating at a given rate.
        """
        if target not in self.__visual_targets__:
            logger.error('Visual target %s not found. Aborting...' % target)
            return

        logger.info('Tracking Moving Point - START - Duration: %.2f, Fixation Time: %.2f' % (track_duration, fixation_time))
        start_time = time.time()
    
        while (time.time() - start_time) < track_duration:
            # Check if stop has been requested
            if self.stop_event.is_set():
                logger.info('Stop signal received. Ending tracking.')
                return False

            # Get the next position from the point generator
            point = self.__visual_targets__[target].get_position()
            if point:
                logger.info('Tracking point: %.2f %.2f %.2f' % (point[0], point[1], point[2]))
                self.observe_points([point], fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout, waitMotionDone=waitMotionDone)
            else:
                logger.warning('No new position available for tracking. Skipping...')

        logger.info('Tracking Moving Point - END')
        return True

    def visual_search_in_workspace(self, center, width, depth, target, num_points=10, fixation_time=2.0, lookat_point_timeout=5.0, timeout=30.0):
        """
        Continuously observe points in the workspace until the target is detected or timeout is reached.
        
        Parameters:
        - center (tuple): The center of the workspace (x, y, z).
        - width (float): The width of the workspace along the y-axis.
        - depth (float): The depth of the workspace along the x-axis.
        - target (str): The name of the visual target to be detected.
        - num_points (int, optional): The number of points to observe. Default is 10.
        - fixation_time (float, optional): Time in seconds the robot should observe each point. Default is 2.0 seconds.
        - lookat_point_timeout (float, optional): Timeout for each point. Default is 5.0 seconds.
        - timeout (float, optional): Maximum time in seconds to search for the target. Default is 30.0 seconds.
        
        Returns:
        - dict: A dictionary containing the positions of the detected target.
        """
        logger.info('Visual Search in Workspace - START - Center: %s, Width: %.2f, Depth: %.2f, Target: %s' % 
                    (center, width, depth, target))

        detected_targets = {}
        start_time = time.time()

        if target in self.targets.keys():
            self.targets[target].flush()

        # Always observe the center point first
        points_to_observe = [center]
        random_points = self.grid_ellipsoid(center, depth / 2, width / 2, 0.05, num_points - 1)  # Generate additional random points
        points_to_observe.extend(random_points)

        while not detected_targets.get(target) and (time.time() - start_time) < timeout:
            for point in points_to_observe:
                # Observe the current point
                detected_targets = self.observe_scene(center=point, width=0, height=0, num_points=1, 
                                                     fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout)
                if detected_targets.get(target):
                    logger.info('Target %s detected at positions: %s' % (target, detected_targets[target]))
                    break
                else:
                    logger.info('Target %s not detected at point %s, continuing observation...' % (target, point))

        # Always observe the center point last if no targets were detected
        if not detected_targets.get(target):
            logger.warning('No target detected, observing the center point one last time.')
            detected_targets = self.observe_scene(center=center, width=0, height=0, num_points=1, 
                                                 fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout)

        if not detected_targets.get(target):
            logger.warning('Target %s not detected within the timeout period of %.2f seconds.' % (target, timeout))

        logger.info('Visual Search in Workspace - END')
        return {target: detected_targets.get(target, [])}


    def visual_search_in_scene(self, center, width, height, target, num_points=10, fixation_time=2.0, lookat_point_timeout=5.0, timeout=30.0):
        """
        Continuously observe points in the scene until the target is detected or timeout is reached.
        
        Parameters:
        - center (tuple): The center of the scene in front of the robot (x, y, z).
        - width (float): The width of the scene along the y-axis.
        - height (float): The height of the scene along the z-axis.
        - target (str): The name of the visual target to be detected.
        - num_points (int, optional): The number of points to observe. Default is 10.
        - fixation_time (float, optional): Time in seconds the robot should observe each point. Default is 2.0 seconds.
        - lookat_point_timeout (float, optional): Timeout for each point. Default is 5.0 seconds.
        - timeout (float, optional): Maximum time in seconds to search for the target. Default is 30.0 seconds.
        
        Returns:
        - dict: A dictionary containing the positions of the detected target.
        """
        logger.info('Visual Search in Scene - START - Center: %s, Width: %.2f, Height: %.2f, Target: %s' % 
                    (center, width, height, target))

        detected_targets = {}
        start_time = time.time()

        if target in self.targets.keys():
            self.targets[target].flush()

        # Always observe the center point first
        points_to_observe = [center]
        random_points = self.grid_ellipsoid(center, width / 2, height / 2, 0.1, num_points - 1)
        points_to_observe.extend(random_points)

        while not detected_targets.get(target) and (time.time() - start_time) < timeout:
            for point in points_to_observe:
                # Observe the current point
                detected_targets = self.observe_scene(center=point, width=0, height=0, num_points=1, 
                                                     fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout)
                if detected_targets.get(target):
                    logger.info('Target %s detected at positions: %s' % (target, detected_targets[target]))
                    break
                else:
                    logger.warning('Target %s not detected at point %s, continuing observation...' % (target, point))

        # Always observe the center point last if no targets were detected
        if not detected_targets.get(target):
            logger.warning('No target detected, observing the center point one last time.')
            detected_targets = self.observe_scene(center=center, width=0, height=0, num_points=1, 
                                                 fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout)

        if not detected_targets.get(target):
            logger.warning('Target %s not detected within the timeout period of %.2f seconds.' % (target, timeout))

        logger.info('Visual Search in Scene - END')
        return {target: detected_targets.get(target, [])}

    def visual_tracking_scene(self, starting_point, target, fixation_time=2.0, lookat_point_timeout=5.0, track_duration=30.0):
        """
        Perform visual search in the scene to detect the target, then start tracking once a stable point is found.
        
        Parameters:
        - starting_point (tuple): The starting point to track (x, y, z).
        - target (str): The name of the visual target to be detected.
        - fixation_time (float, optional): Time in seconds the robot should observe each point. Default is 2.0 seconds.
        - lookat_point_timeout (float, optional): Timeout for each point. Default is 5.0 seconds.
        - track_duration (float, optional): Duration in seconds for tracking the target once detected. Default is 30.0 seconds.
        
        Returns:
        - str: Status of tracking.
        """
        if not self.__lock_tracking__():
            return 'Visual Tracking Scene - ABORTED - Another tracking operation is already active. Cannot start a new tracking operation.'

        logger.info('Visual Tracking Scene - START - Starting Point: %s, Target: %s' % (starting_point, target))

        self.observe_points([starting_point], fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout, waitMotionDone=True)

        logger.info('Tracking Target - START - Target: %s for duration: %.2f seconds' % (target, track_duration))

        res = self.track_moving_point(target, track_duration=track_duration, fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout)

        if res:
            logger.info('Tracking Target - END - Completed duration of %.2f seconds' % track_duration)
        else:
            logger.warning('Tracking Target - END - Stopped on demand before duration completion.')

        self.__release_tracking__()
        return 'Tracking completed or stopped.'

    def visual_tracking_workspace(self, starting_point, target, fixation_time=2.0, lookat_point_timeout=5.0, track_duration=30.0):
        """
        Perform visual search in the workspace to detect the target, then start tracking once a stable point is found.
        
        Parameters:
        - starting_point (tuple): The starting point to track (x, y, z).
        - target (str): The name of the visual target to be detected.
        - fixation_time (float, optional): Time in seconds the robot should observe each point. Default is 2.0 seconds.
        - lookat_point_timeout (float, optional): Timeout for each point. Default is 5.0 seconds.
        - track_duration (float, optional): Duration in seconds for tracking the target once detected. Default is 30.0 seconds.
        
        Returns:
        - str: Status of tracking.
        """
        
        if not self.__lock_tracking__():
            return 'Visual Tracking Workspace - ABORTED - Another tracking operation is already active. Cannot start a new tracking operation.'

        logger.info('Visual Tracking Workspace - START - Starting Point: %s, Target: %s' % (starting_point, target))

        self.observe_points([starting_point], fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout, waitMotionDone=True)
        
        logger.info('Tracking Target - START - Target: %s for duration: %.2f seconds' % (target, track_duration))
        
        res = self.track_moving_point(target, track_duration=track_duration, fixation_time=fixation_time, lookat_point_timeout=lookat_point_timeout)
        
        if res:
            logger.info('Tracking Target - END - Completed duration of %.2f seconds' % track_duration)
        else:
            logger.warning('Tracking Target - END - Stopped on demand before duration completion.')

        self.__release_tracking__()
        return 'Tracking completed or stopped.'


    def __lock_tracking__(self):
        if not self.tracking_lock.acquire(blocking=True):
            logger.warning('Another tracking operation is currently active. Cannot start a new tracking operation.')
            return False
        self.stop_event.clear()
        logger.debug('Tracking started and lock acquired successfully.')
        return True

    def __release_tracking__(self):
        self.tracking_lock.release()
        logger.debug('Tracking lock released successfully.')

    def stop_tracking(self):
        self.stop_event.set()
        self.tracking_lock.acquire()
        self.tracking_lock.release()


    def wait_stable_target(self, target, scene_center, scene_width, scene_height, wait_timeout=10.0, stable_duration=2.0, max_motion_radius=0.05, tracking_timeout=10.0):
        """
        Wait for a visual target to appear, then start tracking until the target is stable for a requested amount of time.

        Parameters:
        - target (str): The name of the visual target to be detected.
        - wait_timeout (float, optional): Maximum time in seconds to wait for the target to appear. Default is 10.0 seconds.
        - stable_duration (float, optional): Duration in seconds that the target needs to stay stable. Default is 1.0 seconds.
        - max_motion_radius (float, optional): Maximum distance in meters that the target can move to be considered stable. Default is 0.05 meters.
        - tracking_timeout (float, optional): Maximum time in seconds for the tracking phase. Default is 10.0 seconds.

        Returns:
        - dict: A dictionary containing the position of the detected target if stable, or an empty list if not detected or not stable.
        """
        if not self.__lock_tracking__():
            return 'Wait Stable Target - ABORTED - Another tracking operation is already active. Cannot start a new tracking operation.'

        logger.info(f'Wait and Track Stable Target - START - Target: {target}, Wait Timeout: {wait_timeout}s, Stable Duration: {stable_duration}s')

        if target not in self.__visual_targets__:
            logger.error(f'Target {target} not found.')
            return {target: []}

        if target in self.targets.keys():
            self.targets[target].flush()

        # Step 1: Wait for the target to appear using the visual search function
        detected_targets = self.visual_search_in_scene(
            center=scene_center,  # Use the robot's default center or defined initial position
            width=scene_width,  # Define an appropriate width for the scene
            height=scene_height,  # Define an appropriate height for the scene
            target=target,
            timeout=wait_timeout,
            fixation_time=0.1,  # Quick fixation time while searching
            lookat_point_timeout=2.0  # Allow a reasonable timeout for looking at each point
        )

        # Check if the target was detected during the search phase
        if not detected_targets.get(target):
            logger.warning(f'Target {target} not detected within wait timeout of {wait_timeout} seconds.')
            return {target: []}

        # Step 2: Track the detected target
        track_start_time = time.time()
        stable_start_time = None
        last_position = detected_targets[target][0] if detected_targets[target] else None

        while (time.time() - track_start_time) < tracking_timeout:
            # Reuse the existing tracking function to track the moving point
            self.track_moving_point(target, track_duration=0.1, fixation_time=0.1, lookat_point_timeout=2.0, waitMotionDone=False)

            # Get the current position of the target
            current_position = self.__visual_targets__[target].get_position()

            if current_position and last_position:
                # Calculate the distance between the current and last known position
                distance = np.linalg.norm(np.array(current_position) - np.array(last_position))

                if distance <= max_motion_radius:
                    # If the target is within the motion radius, check the stability duration
                    if stable_start_time is None:
                        stable_start_time = time.time()  # Start the stability timer

                    if (time.time() - stable_start_time) >= stable_duration:
                        logger.info(f'Target {target} is stable at position: {current_position} for {stable_duration} seconds.')
                        self.observe_points([current_position], fixation_time=0.1, lookat_point_timeout=2.0)
                        self.__release_tracking__()
                        return {target: [current_position]}
                else:
                    # Target moved too much; reset the stability timer
                    logger.info(f'Target {target} moved. Distance: {distance:.2f}m. Resetting stability timer.')
                    stable_start_time = None

                last_position = current_position

            time.sleep(0.1)  # Small delay for tracking updates

        logger.warning(f'Target {target} did not become stable within tracking timeout of {tracking_timeout} seconds.')
        self.__release_tracking__()
        return {target: []}
