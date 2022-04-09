# MIT License
#
# Copyright (c) 2022 Social Cognition in Human-Robot Interaction
#                    Author: Davide De Tommaso (davide.detommaso@iit.it)
#                    Project: Dockyman Template
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

ARG DOCKER_SRC

FROM ${DOCKER_SRC} AS base
LABEL maintainer="Davide De Tommaso <davide.detommaso@iit.it>, Adam Lukomski <adam.lukomski@iit.it>"

ENV DEBIAN_FRONTEND noninteractive

ARG USERNAME
ARG LOCAL_USER_ID
ARG LOCAL_GROUP_ID
ARG GROUP_AUDIO
ARG GROUP_VIDEO
ARG GROUP_INPUT
ARG GROUP_DIALOUT
ARG XDG_RUNTIME_DIR

USER root

ENV USERNAME=${USERNAME}
ENV LOCAL_USER_ID=${LOCAL_USER_ID}
ENV LOCAL_GROUP_ID=${LOCAL_GROUP_ID}
ENV GROUP_INPUT=${GROUP_INPUT}
ENV GROUP_VIDEO=${GROUP_VIDEO}
ENV GROUP_AUDIO=${GROUP_AUDIO}
ENV GROUP_DIALOUT=${GROUP_DIALOUT}

ENV WORKDIR=/home/${USERNAME}
ENV XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR}

RUN if [ $(getent group audio) ]; then groupmod -o audio --gid ${GROUP_AUDIO}; else groupadd audio --gid ${GROUP_AUDIO}; fi
RUN if [ $(getent group video) ]; then groupmod -o video --gid ${GROUP_VIDEO}; else groupadd video --gid ${GROUP_VIDEO}; fi
RUN if [ $(getent group input) ]; then groupmod -o input --gid ${GROUP_INPUT}; else groupadd input --gid ${GROUP_INPUT}; fi
RUN if [ $(getent group dialout) ]; then groupmod -o dialout --gid ${GROUP_DIALOUT}; else groupadd dialout --gid ${GROUP_DIALOUT}; fi

RUN if [ -z "$(getent passwd "${LOCAL_USER_ID}" | cut -d: -f1)" ]; then \
      if [ $(getent passwd ${USERNAME}) ]; then \
          echo "User exists" && usermod -u ${LOCAL_USER_ID} ${USERNAME} && groupmod -g ${LOCAL_GROUP_ID} ${USERNAME} && passwd -d ${USERNAME}; \
      else \
          echo "User not found" && useradd -ms /bin/bash ${USERNAME} && passwd -d ${USERNAME} && usermod -u ${LOCAL_USER_ID} ${USERNAME} && groupmod -g ${LOCAL_GROUP_ID} ${USERNAME}; \
      fi; \
    fi

RUN echo "${USERNAME}:${USERNAME}" | chpasswd
RUN usermod -a -G root,sudo,${GROUP_AUDIO},${GROUP_VIDEO},${GROUP_INPUT},${GROUP_DIALOUT} "$(getent passwd ${LOCAL_USER_ID} | cut -d: -f1)"
RUN chown -R ${LOCAL_USER_ID}:${LOCAL_USER_ID} ${WORKDIR}

RUN rm /var/log/lastlog /var/log/faillog /var/log/dpkg.log
WORKDIR ${WORKDIR}

ENV PATH=${PATH}:~/.local/bin:${WORKDIR}
RUN mkdir -p ${XDG_RUNTIME_DIR} && chown ${LOCAL_USER_ID}:${LOCAL_USER_ID} ${XDG_RUNTIME_DIR}

USER ${LOCAL_USER_ID}
