#!/bin/bash

set -e

source "$(dirname "$0")/setup.sh"

docker compose --profile test up --build pyicub.test

docker compose --profile test down --remove-orphans