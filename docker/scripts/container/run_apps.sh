#!/bin/bash

source "$(dirname "$0")/common.sh"

initialize_environment

source $(dirname "$0")/setup.sh

terminator 2>/dev/null &

start_local_yarprun

echo "Launching yarpmanager..."
yarpmanager --apppath "${ICUB_APPS}/applications" --from "${ICUB_APPS}/applications/cluster-config.xml"
