#!/bin/bash

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export XP_SCRIPT_DIR=${CURRENT_DIR}
export XP_TARGET_DIR=${CURRENT_DIR}/..

bash ${XP_SCRIPT_DIR}/build.sh setup
bash ${XP_SCRIPT_DIR}/build.sh local

export BASE_SERVICE_NAME=base

if [[ $(lsmod | grep nvidia) ]]; then
  export BASE_SERVICE_FILENAME=${XP_TARGET_DIR}/.dockyman/compose/nvidia.yml
else
  export BASE_SERVICE_FILENAME=${XP_TARGET_DIR}/.dockyman/compose/base.yml
fi

docker-compose -f ${XP_TARGET_DIR}/docker-compose.yml $@ up
docker-compose -f ${XP_TARGET_DIR}/docker-compose.yml $@ down --remove-orphans
