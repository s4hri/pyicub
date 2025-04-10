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

To test the pyicub repository, follow these steps:

1. Clone the testing repository:
    ```
    git clone -b pyicub-ubuntu22.04-robotologyv2024.x https://github.com/s4hri/s4hri-docker.git
    ```

2. Navigate to the cloned directory:
    ```
    cd s4hri-docker/
    ```

3. Update the environment variables in the `dockyman.env` file:
    - **PYICUB_URL**: Set this to the URL of the pyicub repository you want to test.
    - **PYICUB_BRANCH**: Set this to the branch of the pyicub repository you want to test.
    - **COMPOSE_PROFILE**: Set this to `test`.

4. Run the following command to execute the test:
    ```
    bash go
    ```


Acknowledgments
-------------

- pyicub logo inspired by [iCubArtwork](https://github.com/alecive/iCubArtwork)
