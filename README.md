![PYICUB logo](media/pyicub-logo.png?raw=true)
====

Introduction
-------------
[PYICUB](https://github.com/s4hri/pyicub) is a framework for developing iCub applications using Python.


Documentation
--------------
For usage examples, check out the [Examples Documentation](https://s4hri.github.io/pyicub/).

Requirements
-------------
- [YARP](https://github.com/robotology/yarp) (compiled with Python wrappers)
- [icub-main](https://github.com/robotology/icub-main)


How to install the Python package
-------------
```
git clone https://github.com/s4hri/pyicub
cd pyicub
pip3 install .
```

Quick start (using Docker)
-------------
In order to simplify the installation procedure, we have containerized the
essential requirements in a Docker image including YARP and icub-main.

[PYICUB-LAB](https://github.com/s4hri/pyicub-lab) is a development platform
for coding iCub applications in minutes! Try it now and leave your feedback!

```
git clone https://github.com/s4hri/pyicub-lab
cd pyicub-lab
bash go
```

How to test pyicub
-------------

To run the tests:

1. Run pytest from the main directory:
    ```
    pytest -v
    ```

Acknowledgments
-------------

- pyicub logo inspired by [iCubArtwork](https://github.com/alecive/iCubArtwork)
