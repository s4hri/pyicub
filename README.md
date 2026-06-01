PyiCub
====

Introduction
-------------
[PYICUB](https://github.com/s4hri/pyicub) is a framework for developing iCub applications using Python.


Documentation
--------------
The official documentation is available at [PyiCub Documentation](https://pyicub-doc.readthedocs.io/en/latest/).


Requirements
-------------
- [YARP](https://github.com/robotology/yarp) (compiled with Python wrappers)
- [icub-main](https://github.com/robotology/icub-main)


How to install the Python package
-------------
```
git clone git@github.com:s4hri/pyicub.git
cd pyicub
pip3 install .
```

How to start (using Docker)
-------------
In order to simplify the installation procedure, we have containerized the essential requirements in a Docker image.

```
git clone git@github.com:s4hri/pyicub.git
cd pyicub/docker
bash build.sh
bash run.sh
```

How to test pyicub
-------------

To run the tests, use the dedicated script from your host machine. It will build the image, start a headless simulation container, wait for it to be healthy, run the test container, and tear everything down on completion.

```
cd pyicub/docker
bash run_tests.sh
```

The test results (HTML report) are written to `docker/shared/pytest/pytest_report.html`.
