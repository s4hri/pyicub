ARG DOCKER_SRC

FROM $DOCKER_SRC

LABEL maintainer="Davide De Tommaso <davide.detommaso@iit.it>"

ARG PYICUB_TAG
ARG PYICUB_BRANCH

WORKDIR /home/icub

USER icub

ENV PATH=$PATH:/home/icub/.local/bin

RUN cd /home/icub && \
    git clone https://github.com/s4hri/pyicub -b ${PYICUB_BRANCH} && \
    cd pyicub && \
    git checkout ${PYICUB_TAG} && \
    pip3 install -r requirements.txt

ENV PYTHONPATH $PYTHONPATH:/home/icub/pyicub
ENV YARP_COLORED_OUTPUT 1
