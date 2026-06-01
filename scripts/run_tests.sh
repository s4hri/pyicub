#!/bin/bash

source "$(dirname "$0")/common.sh"

initialize_environment
check_existing_yarpserver
cd $ROBOT_CODE/pyicub

exec pytest --html=$PYTEST_OUTPUT_DIR/pytest_report.html
