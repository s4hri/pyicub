#!/bin/bash

source "$(dirname "$0")/common.sh"

initialize_environment
source "$(dirname "$0")/setup.sh"

PYICUB_ENV_FILE="$HOME/.pyicub_env"
BASHRC_FILE="$HOME/.bashrc"

if [[ "${YARP_SERVER}" == "true" ]]; then
  start_yarpserver_detached
else
  check_existing_yarpserver
fi

start_local_yarprun

if [[ "${ICUB_SIMULATION}" == "false" ]]; then
  if wait_for_icub_host 5; then
    ensure_ssh_key_installed
    start_icub_yarprun
    export ICUB_NAME=icub
  else
    exit 1;
  fi
else
  export ICUB_NAME=icubSim
fi


# Save environment variables
echo "Writing environment variables to $PYICUB_ENV_FILE"
{
  echo "export ICUB_SIMULATION=$ICUB_SIMULATION"
  echo "export ICUB_NAME=$ICUB_NAME"
  echo "export ICUB_APPS=${ICUB_APPS}"
} > "$PYICUB_ENV_FILE"

# Inject into .bashrc if not already present
if ! grep -q 'source ~/.pyicub_env' "$BASHRC_FILE"; then
  echo -e "\n# Load PyiCub environment automatically" >> "$BASHRC_FILE"
  echo "source ~/.pyicub_env" >> "$BASHRC_FILE"
  echo "Added environment loader to $BASHRC_FILE"
else
  echo "Environment loader already present in $BASHRC_FILE"
fi

terminator 2>/dev/null &

echo "Launching yarpmanager..."
yarpmanager --apppath "${ICUB_APPS}/applications" --from "${ICUB_APPS}/applications/cluster-config.xml"

if [[ "${ICUB_SIMULATION}" == "false" ]]; then
  cleanup_remote_processes
fi
