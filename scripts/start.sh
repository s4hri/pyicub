#!/bin/bash

source "$(dirname "$0")/common.sh"

initialize_environment
source "$(dirname "$0")/setup.sh"

PYICUB_ENV_FILE="$HOME/.pyicub_env"
BASHRC_FILE="$HOME/.bashrc"


start_yarpserver_detached
start_local_yarprun

if wait_for_icub_host 3; then
  ensure_ssh_key_installed
  start_icub_yarprun
  export ICUB_SIMULATION=false
  export ICUB_NAME=icub
else
  export ICUB_SIMULATION=true
  export ICUB_NAME=icubSim
fi

terminator 2>/dev/null &

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



echo "Launching yarpmanager..."
yarpmanager --apppath "${ICUB_APPS}/applications" --from "${ICUB_APPS}/applications/cluster-config.xml"

if [ "$ICUB_SIMULATION" = false ]; then
  cleanup_remote_processes
fi
