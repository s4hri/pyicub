#!/bin/bash

set -e

echo "Initializing..."

# Source environment setup
source "${ROBOTOLOGY_SUPERBUILD_INSTALL_DIR}/share/robotology-superbuild/setup.sh"

# Function to check if 'test' is one of the comma-separated profiles
contains_test_profile() {
  [[ ",$COMPOSE_PROFILES," == *",test,"* ]]
}

if contains_test_profile; then
  echo "Test profile detected."
  /workspace/icub-entrypoint/scripts/run_tests.sh
else
  echo "Running normal environment."
  /workspace/icub-entrypoint/scripts/run_env.sh
fi
