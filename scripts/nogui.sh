#!/bin/bash

source "$(dirname "$0")/common.sh"
export ICUB_NAME=icubSim
export DISPLAY=:99
sudo Xvfb :99 -screen 0 1024x768x24 &
sleep 1  # Give it time to start

initialize_environment
start_yarpserver_detached >/dev/null 2>&1
start_local_yarprun >/dev/null 2>&1

SIM_APP_XML="${ICUB_APP_XML:-${ICUB_APPS}/applications/icubSim/icub-gazebo.xml}"
yarpmanager-console --application "$SIM_APP_XML" --run --connect