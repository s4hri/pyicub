#!/bin/bash

echo "Initializing environment..."

source ${ROBOTOLOGY_SUPERBUILD_INSTALL_DIR}/share/robotology-superbuild/setup.sh

# ===============================
# TEST MODE BLOCK (early exit)
# ===============================
if [ "${COMPOSE_PROFILES:-test}" = "test" ]; then
  echo "Test Profile is enabled. Running test setup..."

  # Start yarpserver
  echo "Starting yarpserver..."
  YARP_FORWARD_LOG_ENABLE=0 yarpserver --write >/dev/null 2>&1 &
  sleep 2

  # Start local yarprun
  yarprun --server /"$ICUBSRV_NODE" --log >/dev/null 2>&1 &
  sleep 2

  echo "Starting Gazebo simulation..."
  gzserver /workspace/icub-apps/gazebo/icub-world.sdf >/dev/null 2>&1 &
  sleep 2

  echo "Starting robot interface..."
  yarprobotinterface --context gazeboCartesianControl --config no_legs.xml --portprefix /iCubSim >/dev/null 2>&1 &
  sleep 2

  echo "Running pytest..."
  cd /workspace/pyicub|| exit 1
  pytest --html=/workspace/test-reports/report.html

  echo "Tests completed. Exiting."
  exit 0
fi

# ===============================
# NORMAL MODE CONTINUES HERE
# ===============================

terminator 2>/dev/null &

  # Start yarpserver
  echo "Starting yarpserver..."
  YARP_FORWARD_LOG_ENABLE=0 yarpserver --write &
  sleep 2

if [ "${ICUB_SIMULATION:-false}" != "true" ]; then
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

  echo -e "\n$ICUB_HOST is reachable. Starting remote yarprun..."
  sshpass -p 'icub' ssh -o StrictHostKeyChecking=no icub@"$ICUB_HOST" \
    "nohup yarprun --server /$ICUB_NODE --log > yarprun.log 2>&1 &" &
fi

# Start local yarprun
yarprun --server /"$ICUBSRV_NODE" --log &
sleep 2

# Launch yarpmanager
echo "Launching yarpmanager..."
yarpmanager --apppath "${ICUB_APPS}/applications" --from "${ICUB_APPS}/applications/cluster-config.xml"

# Clean up remote if needed
if [ "${ICUB_SIMULATION:-false}" != "true" ]; then
  echo "Cleaning up remote processes..."
  sshpass -p 'icub' ssh -o StrictHostKeyChecking=no icub@"$ICUB_HOST" \
    "killall -q -9 yarprun yarpdev || true"
fi
