#!/bin/bash
terminator 2>/dev/null &

source "$(dirname "$0")/common.sh"

initialize_environment

source $(dirname "$0")/setup.sh

if [ "${ICUB_SIMULATION:-true}" != "true" ]; then
  wait_for_icub_host
  ensure_ssh_key_installed
else
  echo "Running in simulation..."
fi

start_yarpserver_detached

start_icub_yarprun

start_local_yarprun

echo "Launching yarpmanager..."
yarpmanager --apppath "${ICUB_APPS}/applications" --from "${ICUB_APPS}/applications/cluster-config.xml"

if [ "${ICUB_SIMULATION:-true}" != "true" ]; then
  cleanup_remote_processes
fi
