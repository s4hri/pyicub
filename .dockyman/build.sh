#!/bin/bash

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export XP_SCRIPT_DIR=${CURRENT_DIR}
export XP_TARGET_DIR=${CURRENT_DIR}/..

make --makefile=${XP_SCRIPT_DIR}/Makefile "$@"
