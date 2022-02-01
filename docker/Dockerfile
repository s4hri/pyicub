ARG DOCKER_SRC

FROM $DOCKER_SRC

LABEL maintainer="Davide De Tommaso <davide.detommaso@iit.it>"

ARG PYICUB_VER
ARG WORKDIR

ENV WORKDIR ${WORKDIR}
USER docky

RUN cd ${WORKDIR} && \
    git clone https://github.com/s4hri/pyicub -b ${PYICUB_VER} && \
    cd pyicub/pyicub && \
    pip3 install -r requirements.txt

ENV PYTHONPATH $PYTHONPATH:${WORKDIR}/pyicub
ENV YARP_FORWARD_LOG_ENABLE 1
