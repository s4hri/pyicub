#!/bin/bash

set -e

initialize_environment() {
  echo "Initializing environment..."
  source "${ROBOTOLOGY_SUPERBUILD_INSTALL_DIR}/share/robotology-superbuild/setup.sh"
}

wait_for_icub_host() {
  local timeout="${1:-60}"
  echo "Waiting for $ICUB_HOST to become reachable (timeout: ${timeout}s)..."
  local seconds_waited=0

  while ! ping -c 1 -W 1 "$ICUB_HOST" >/dev/null 2>&1; do
    printf "."

    if command -v play >/dev/null 2>&1; then
      play -n synth 0.1 sin 440 >/dev/null 2>&1
    else
      printf "\a"
    fi
    sleep 1;


    seconds_waited=$((seconds_waited + 1))

    if [ "$seconds_waited" -ge "$timeout" ]; then
      echo -e "\n$ICUB_HOST not reachable within timeout."
      return 1
    fi
  done

  echo -e "\n$ICUB_HOST is reachable."

  if command -v play >/dev/null 2>&1; then
    play -n synth 0.5 sin 880 >/dev/null 2>&1
  else
    printf "\a"
  fi

  return 0
}



start_yarpserver() {
  echo "Starting yarpserver..."
  YARP_FORWARD_LOG_ENABLE=0 yarpserver --write
}

start_yarpserver_detached() {
  echo "Starting yarpserver (detached)..."
  YARP_FORWARD_LOG_ENABLE=0 yarpserver --write &
  sleep 2
}

start_local_yarprun() {
  echo "Starting local yarprun..."
  yarprun --server /"$PYICUB_NODE" --log &
  sleep 2
}

start_icub_yarprun() {
  echo -e "\nStarting remote yarprun on $ICUB_HOST..."
  ssh icub@"$ICUB_HOST" \
    "nohup yarprun --server /$ICUB_NODE --log &" &
  sleep 2
}

cleanup_remote_processes() {
  echo "Cleaning up remote processes on $ICUB_HOST..."
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

check_existing_yarpserver() {
  for i in {1..5}; do
    if yarp detect --write >/dev/null 2>&1; then
      echo "Existing yarpserver detected."
      return
    else
      echo "No yarpserver detected. Attempt $i of 5."
      sleep 2
    fi
  done
}