#!/bin/bash

set -e

initialize_environment() {
  echo "Initializing environment..."
  source "${ROBOTOLOGY_SUPERBUILD_INSTALL_DIR}/share/robotology-superbuild/setup.sh"
}

start_yarpserver() {
  echo "Starting yarpserver..."
  YARP_FORWARD_LOG_ENABLE=0 yarpserver --write
}

start_yarpserver_detached() {
  echo "Starting yarpserver..."
  YARP_FORWARD_LOG_ENABLE=0 yarpserver --write &
  sleep 2
}

start_local_yarprun() {
  echo "Starting local yarprun..."
  yarprun --server /"$ICUBSRV_NODE" --log &
  sleep 2
}

start_icub_yarprun() {
  echo -e "\n$ICUB_HOST is reachable. Starting remote yarprun..."
  ssh icub@"$ICUB_HOST" \
    "nohup yarprun --server /$ICUB_NODE --log &" &
  sleep 2
}

wait_for_icub_host() {
  echo "Waiting for $ICUB_HOST to become reachable..."
  TIMEOUT=60
  SECONDS_WAITED=0

  until ping -c 1 -W 1 "$ICUB_HOST" >/dev/null 2>&1; do
    printf "."
    sleep 1
    SECONDS_WAITED=$((SECONDS_WAITED + 1))
    if [ $SECONDS_WAITED -ge $TIMEOUT ]; then
      echo -e "\nTimeout waiting for $ICUB_HOST. Exiting."
      exit 1
    fi
  done
}

cleanup_remote_processes() {
  echo "Cleaning up remote processes..."
  ssh icub@"$ICUB_HOST" \
    "killall -q -9 yarprun yarpdev || true"
}

ensure_ssh_key_installed() {
  echo "Checking SSH key access to $ICUB_HOST..."

  if ssh -o BatchMode=yes -o ConnectTimeout=5 icub@"$ICUB_HOST" 'exit'; then
    echo "SSH key already installed."
    return
  fi

  echo "SSH key not found. Attempting to copy SSH key to icub@$ICUB_HOST"
  if [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo "No SSH key found. Generating one..."
    ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa
  fi

  echo "You may be prompted for the icub user's password to copy the key."
  ssh-copy-id -o StrictHostKeyChecking=no icub@"$ICUB_HOST"
}
