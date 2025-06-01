#!/bin/bash

source "$(dirname "$0")/common.sh"

export DISPLAY=:99
sudo Xvfb :99 -screen 0 1024x768x24 &
sleep 1  # Give it time to start

initialize_environment
start_yarpserver_detached >/dev/null 2>&1
start_local_yarprun >/dev/null 2>&1

echo "Starting Gazebo simulation..."
gzserver ${ICUB_APPS}/gazebo/icub-world.sdf >/dev/null 2>&1 &
sleep 5

echo "Starting robot interface..."
yarprobotinterface --context gazeboCartesianControl --config no_legs.xml --portprefix /icubSim >/dev/null 2>&1 &
sleep 5

echo "Running pytest..."
cd $ROBOT_CODE/pyicub || exit 1

pytest --html=$PYTEST_OUTPUT_DIR/pytest_report.html
