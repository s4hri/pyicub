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

source ${XP_TARGET_DIR}/.env

LOCAL_USER_ID=$(id -u)
LOCAL_GROUP_ID=$(id -g)
GROUP_AUDIO=$(getent group audio | cut -d: -f3)
GROUP_VIDEO=$(getent group video | cut -d: -f3)
GROUP_INPUT=$(getent group input | cut -d: -f3)
GROUP_DIALOUT=$(getent group dialout | cut -d: -f3)

export LOCAL_USER_ID
export LOCAL_GROUP_ID
export GROUP_AUDIO
export GROUP_VIDEO
export GROUP_INPUT
export GROUP_DIALOUT
export PJT_DOCKER_IMAGE


ID=$(lsb_release -is | tr '[:upper:]' '[:lower:]')
VERSION_ID=$(lsb_release -rs)

export ID
export VERSION_ID

install_reqs()
{
	echo "Checking Docker ..."
	if which docker
  then
	    echo "docker found, skipping"
	else
	    echo "docker not found, installing"
	    if -e /etc/os-release
      then
	        if cat /etc/os-release | grep Ubuntu
          then
	            echo "Found Ubuntu, proceeding with docker-ce install"
	            echo "sudo apt update"
	            sudo apt update
	            sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release
	            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	            sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu
	             `lsb_release -cs` stable"
	            sudo apt update
	            sudo apt-get install docker-ce docker-ce-cli containerd.io
	            sudo usermod -aG docker ${USER}
	        else
	            echo "Only Ubuntu is supported for apt installs, skipping"
	        fi
	    fi
	fi
	echo "Checking docker-compose ..."
	if which docker-compose
  then
	    echo "docker-compose found, skipping"
	else
	    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-`uname -s`-`uname -m`" -o /usr/local/bin/docker-compose
	    sudo chmod 777 /usr/local/bin/docker-compose
	fi
	echo "Checking nvidia container runtime ..."
	if lsmod | grep nvidia
  then
	    echo "found nvidia card drivers"
		if which nvidia-container-runtime-hook
    then
	        echo "found nvidia container runtime, skipping"
	    else
	        if -e /etc/os-release
          then
	            if cat /etc/os-release | grep Ubuntu
              then
	                echo "Adding nvidia apt repository for ${ID}${VERSION_ID}"
	                curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey |   sudo apt-key add -
	                curl -s -L https://nvidia.github.io/nvidia-container-runtime/${ID}${VERSION_ID}/nvidia-container-runtime.list |   sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
	                sudo apt-get update
	                sudo apt install nvidia-container-runtime
	            else
	                echo "Only Ubuntu is supported for apt installs, skipping"
	            fi
	        fi
		fi
	fi
	echo "Checking if user in group docker ..."
	if groups | grep -o docker
  then
	    echo "user ${USER} already in group docker"
	else
	    sudo usermod -aG docker ${USER}
			echo "!!! Please reboot your computer for these changes to take effect!!!"
	fi
	echo "All Docker requirements are satisfied!"
}

install_reqs
