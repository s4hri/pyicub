#!/bin/bash

source "$(dirname "$0")/common.sh"

initialize_environment

if [ "${ICUB_SIMULATION:-true}" != "true" ]; then
  ensure_ssh_key_installed
  wait_for_icub_host
else
  echo "Running in simulation..."
fi

start_yarpserver

if [ "${ICUB_SIMULATION:-true}" != "true" ]; then
  cleanup_remote_processes
fi
