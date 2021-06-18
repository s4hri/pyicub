.PHONY: setup clean_dist distro clean install uninstall test docker_build docker_run

NAME='pyicub'
VERSION=`python3 setup.py -V`

LOCAL_USER_ID := $(shell id -u)
export LOCAL_USER_ID

setup:
	echo "Building PyiCub version ${VERSION}"

clean_dist:
	-rm -f MANIFEST
	-rm -rf dist
	-rm -rf deb_dist
	-rm -rf build
	-rm -rf pyicub.egg-info

distro: setup clean_dist
	python3 setup.py sdist

clean: clean_dist
	echo "clean"

install: distro
	python3 -m pip install --user .

uninstall:
	python3 -m pip uninstall pyicub

test:
	python3 -m unittest discover -s tests

docker_build:
	docker-compose -f docker/docker-compose.yml build

docker_run: docker_build
	docker-compose -f docker/docker-compose.yml up --remove-orphans
