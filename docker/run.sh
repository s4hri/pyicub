#!/bin/bash

set -e

source "$(dirname "$0")/setup.sh"

docker compose up

docker compose down --remove-orphans