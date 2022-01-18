#!/bin/bash

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export XP_SCRIPT_DIR=${CURRENT_DIR}
export XP_TARGET_DIR=${CURRENT_DIR}/..

bash ${XP_SCRIPT_DIR}/build.sh local
bash ${XP_SCRIPT_DIR}/init.sh
docker-compose -f ${XP_TARGET_DIR}/docker-compose.yml up
docker-compose -f ${XP_TARGET_DIR}/docker-compose.yml down
