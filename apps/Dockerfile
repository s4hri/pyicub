ARG SRC_IMAGE
FROM $SRC_IMAGE

LABEL maintainer="Davide De Tommaso <davide.detommaso@iit.it>"
ARG LOCAL_USER_ID

ENV DEBIAN_FRONTEND noninteractive

USER root

RUN usermod -u ${LOCAL_USER_ID} docky

USER docky
