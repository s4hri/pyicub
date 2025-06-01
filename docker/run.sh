#!/bin/bash

set -e

source "$(dirname "$0")/setup.sh"

LOCAL_USER_UID=$(id -u) LOCAL_USER_GID=$(id -g) docker compose up

LOCAL_USER_UID=$(id -u) LOCAL_USER_GID=$(id -g) docker compose down --remove-orphans