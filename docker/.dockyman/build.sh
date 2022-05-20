# MIT License
#
# Copyright (c) 2022 Social Cognition in Human-Robot Interaction
#                    Author: Davide De Tommaso (davide.detommaso@iit.it)
#                    Project: Dockyman Template
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#!/bin/bash

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export XP_SCRIPT_DIR=${CURRENT_DIR}
export XP_TARGET_DIR=${CURRENT_DIR}/..

source ${XP_SCRIPT_DIR}/setup.sh

base()
{
  echo "Building project docker image ${PJT_DOCKER_IMAGE}"
  docker-compose -f ${XP_TARGET_DIR}/docker-compose.base.yml build $1
}

local()
{
  echo "Retrieving docker image ${PJT_DOCKER_IMAGE} and building local docker image ${LOCAL_DOCKER_IMAGE}, USERNAME: ${USERNAME}, LOCAL_UID: ${LOCAL_USER_ID}, GROUP_AUDIO: ${GROUP_AUDIO}, GROUP_VIDEO: ${GROUP_VIDEO}, GROUP_INPUT: ${GROUP_INPUT}, GROUP_DIALOUT: ${GROUP_DIALOUT}"
  docker-compose -f ${XP_TARGET_DIR}/docker-compose.yml build $1
}

distro()
{
  echo "Pushing docker image ${PJT_DOCKER_IMAGE} ..."
  docker-compose -f ${XP_TARGET_DIR}/docker-compose.base.yml push
}


for var in "$@"
  do
    if [ $var = "--no-cache" ]
    then
      NO_CACHE="--no-cache"
    else
      NO_CACHE=""
    fi
done

if [ "$1" = "--no-cache" ]
then
  docker system prune
  docker-compose -f ${XP_TARGET_DIR}/docker-compose.yml down -v --remove-orphans --rmi all
  docker-compose -f ${XP_TARGET_DIR}/docker-compose.yml down -v --remove-orphans --rmi all
  base $NO_CACHE
  local $NO_CACHE
else
  if [ -z "$1" ]
  then
    base
    local
  fi
fi


for var in "$@"
  do
    if [ $var = "base" ]
      then
        base $NO_CACHE
    fi
    if [ $var = "local" ]
      then
        local $NO_CACHE
    fi
    if [ $var = "distro" ]
      then
        distro
    fi
done
