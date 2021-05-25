.PHONY: all setup clean_dist distro clean install uninstall testsetup test

NAME='pyicub'
VERSION=`python3 setup.py -V`

all:
	echo "noop for debbuild"

setup:
	echo "building version ${VERSION}"

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
	sudo checkinstall --default --backup=no --nodoc --deldoc=yes --deldesc=yes --delspec=yes --pakdir=/tmp python3 setup.py install

uninstall:
	dpkg -r pyicub

testsetup:
	echo "running pyicub tests"

test: testsetup
	nosetests --with-coverage --cover-package=pyicub --with-xunit test
