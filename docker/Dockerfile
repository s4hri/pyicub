ARG DOCKER_SRC

FROM $DOCKER_SRC

LABEL maintainer="Davide De Tommaso <davide.detommaso@iit.it>"

ARG PYICUB_TAG

USER docky

RUN cd ${HOME} && \
    git clone https://github.com/s4hri/pyicub && \
    cd pyicub && \
    git fetch --all --tags && \
    git checkout ${PYICUB_TAG} && \
    pip3 install --user -r requirements.txt

ENV PYTHONPATH ${PYTHONPATH}:/home/docky/pyicub

ENTRYPOINT ["bash"]
