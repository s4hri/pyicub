#!/bin/bash

set -e

source "$(dirname "$0")/setup.sh"

cleanup() {
	docker compose --profile test down --remove-orphans
}

trap cleanup EXIT

docker compose --profile test up --build --abort-on-container-exit --exit-code-from pyicub.test pyicub.test