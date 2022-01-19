ARG DOCKER_SRC

FROM $DOCKER_SRC

LABEL maintainer="Davide De Tommaso <davide.detommaso@iit.it>"

ARG PYICUB_VER
ARG WORKDIR
ARG PYTHON_PACKAGES_DIR

USER root


RUN cd ${WORKDIR} && \
    git clone https://github.com/s4hri/pyicub -b ${PYICUB_VER} && \
    cd pyicub && \
    pip3 install --target=${PYTHON_PACKAGES_DIR} -r requirements.txt;

ENV PYTHON_PACKAGES_DIR ${PYTHON_PACKAGES_DIR}
ENV PYTHONPATH ${PYTHONPATH}:${PYTHON_PACKAGES_DIR}:${WORKDIR}/pyicub
