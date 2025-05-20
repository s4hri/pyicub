#!/bin/bash

source "$(dirname "$0")/common.sh"

initialize_environment
start_yarpserver >/dev/null 2>&1
start_local_yarprun >/dev/null 2>&1

echo "Starting Gazebo simulation..."
gzserver ${ICUB_APPS}/gazebo/icub-world.sdf >/dev/null 2>&1 &
sleep 2

echo "Starting robot interface..."
yarprobotinterface --context gazeboCartesianControl --config no_legs.xml --portprefix /iCubSim >/dev/null 2>&1 &
sleep 2

echo "Running pytest..."
cd /workspace/pyicub || exit 1
pytest --html=/var/test-reports/report.html
