ARG DOCKER_SRC

FROM $DOCKER_SRC

LABEL maintainer="Davide De Tommaso <davide.detommaso@iit.it>"

ARG PYICUB_VER
ARG WORKDIR

USER root

RUN cd ${WORKDIR} && \
    git clone https://github.com/s4hri/pyicub -b ${PYICUB_VER} && \
    cd pyicub && \
    pip3 install --target=/usr/local/lib/python3.8/dist-packages -r requirements.txt;

ENV PYTHONPATH ${PYTHONPATH}:${WORKDIR}/pyicub
