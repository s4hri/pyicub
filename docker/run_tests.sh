#!/bin/bash

set -e

source "$(dirname "$0")/setup.sh"

docker compose --profile simulation_nogui up --build -d

docker compose --profile test up --build pyicub.test

docker container stop pyicub-simulation-nogui

docker compose --profile test down --remove-orphans
