LOCAL_USER_ID := $(shell id -u)
DOCKER_USERNAME := docky
GROUP_AUDIO := $(shell getent group audio | cut -d: -f3)
GROUP_VIDEO := $(shell getent group video | cut -d: -f3)
GROUP_INPUT := $(shell getent group input | cut -d: -f3)


export LOCAL_USER_ID
export DOCKER_USERNAME
export GROUP_AUDIO
export GROUP_VIDEO
export GROUP_INPUT

include ${XP_TARGET_DIR}/.env

SHELL := /bin/bash

PJT_DOCKER_IMAGE := ${DOCKER_DOMAIN}/${PROJECT_NAME}-docker:${RELEASE}
export PJT_DOCKER_IMAGE

CONTAINER_NAME := ${PROJECT_NAME}.${RELEASE}.local
export CONTAINER_NAME
LOCAL_DOCKER_IMAGE := ${PJT_DOCKER_IMAGE}.local

ifeq (, $(shell lsmod | grep nvidia))
	NVIDIA_ENV := 0
else
	NVIDIA_ENV := 1
endif

export NVIDIA_ENV
export LOCAL_DOCKER_IMAGE

ID := $(shell lsb_release -is | tr '[:upper:]' '[:lower:]')
VERSION_ID := $(shell lsb_release -rs)
export ID
export VERSION_ID

define install_reqs
	@echo "Checking Docker ..."
	@(if which docker; then \
	    echo "docker found, skipping"; \
	else \
	    echo "docker not found, installing"; \
	    if [ -e /etc/os-release ]; then \
	        if cat /etc/os-release | grep Ubuntu; then \
	            echo "Found Ubuntu, proceeding with docker-ce install"; \
	            echo "sudo apt update"; \
	            sudo apt update; \
	            sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release; \
	            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - ; \
	            sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
	             `lsb_release -cs` stable"; \
	            sudo apt update; \
	            sudo apt-get install docker-ce docker-ce-cli containerd.io; \
	            sudo usermod -aG docker ${USER}; \
	        else \
	            echo "Only Ubuntu is supported for apt installs, skipping"; \
	        fi; \
	    fi; \
	fi)
	@echo "Checking docker-compose ..."
	@(if which docker-compose; then \
	    echo "docker-compose found, skipping"; \
	else \
	    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-`uname -s`-`uname -m`" -o /usr/local/bin/docker-compose; \
	    sudo chmod 777 /usr/local/bin/docker-compose ; \
	fi )
	@echo "Checking nvidia container runtime ..."
	@(if lsmod | grep nvidia; then \
	    echo "found nvidia card drivers"; \
		if which nvidia-container-runtime-hook; then \
	        echo "found nvidia container runtime, skipping"; \
	    else \
	        if [ -e /etc/os-release ]; then \
	            if cat /etc/os-release | grep Ubuntu; then \
	                echo "Adding nvidia apt repository for ${ID}${VERSION_ID}" ; \
	                curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey |   sudo apt-key add -; \
	                curl -s -L https://nvidia.github.io/nvidia-container-runtime/${ID}${VERSION_ID}/nvidia-container-runtime.list |   sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list; \
	                sudo apt-get update; \
	                sudo apt install nvidia-container-runtime; \
	            else \
	                echo "Only Ubuntu is supported for apt installs, skipping"; \
	            fi; \
	        fi; \
		fi; \
	fi )
	@echo "Checking if user in group docker ..."
	@(if groups | grep -o docker; then \
	    echo "user ${USER} already in group docker"; \
	else \
	    sudo usermod -aG docker ${USER}; \
	fi )
	@echo "All Docker requirements are satisfied!"
endef

.DEFAULT_GOAL := all
.PHONY : all clean setup docker local distro

all: setup clean docker local

clean:
	docker system prune

	@(if docker images --format "{{.Repository}}:{{.Tag}}" | grep "${LOCAL_DOCKER_IMAGE}"; then \
			echo "Removing local docker image ${LOCAL_DOCKER_IMAGE}"; \
			docker image rm ${LOCAL_DOCKER_IMAGE}; \
	fi)

	@(if docker images --format "{{.Repository}}:{{.Tag}}" | grep "${PJT_DOCKER_IMAGE}"; then \
	    echo "Removing project docker image ${PJT_DOCKER_IMAGE}"; \
	    docker image rm ${PJT_DOCKER_IMAGE}; \
	fi)

setup:
	@echo "Checking requirements ..."
	$(call install_reqs)


docker: setup
	echo "Building project docker image ${PJT_DOCKER_IMAGE}"; \
	docker build ${XP_TARGET_DIR}/docker -t ${PJT_DOCKER_IMAGE} --build-arg DOCKER_SRC=${DOCKER_SRC} ${BUILD_ARGS};

local:
	echo "Pulling docker image ${PJT_DOCKER_IMAGE} and building local docker image ${LOCAL_DOCKER_IMAGE}, USER: ${DOCKER_USERNAME}, LOCAL_UID: ${LOCAL_USER_ID}, GROUP_AUDIO: ${GROUP_AUDIO}, GROUP_VIDEO: ${GROUP_VIDEO}, GROUP_INPUT: ${GROUP_INPUT}";
	docker build ${XP_SCRIPT_DIR} \
			-t ${LOCAL_DOCKER_IMAGE} \
			--build-arg USER=${DOCKER_USERNAME} \
			--build-arg DOCKER_SRC=${PJT_DOCKER_IMAGE} \
			--build-arg LOCAL_USER_ID=${LOCAL_USER_ID} \
			--build-arg GROUP_AUDIO=${GROUP_AUDIO} \
			--build-arg GROUP_VIDEO=${GROUP_VIDEO} \
			--build-arg GROUP_INPUT=${GROUP_INPUT} \
			--build-arg WORKDIR=${WORKDIR};

distro: docker
	@echo "Pushing docker image ${PJT_DOCKER_IMAGE} on ${DOCKER_DOMAIN}"
	docker push ${PJT_DOCKER_IMAGE}
	docker tag ${PJT_DOCKER_IMAGE} ${DOCKER_DOMAIN}/${PROJECT_NAME}-docker:latest
	docker push ${DOCKER_DOMAIN}/${PROJECT_NAME}-docker:latest
