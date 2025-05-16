#!/bin/bash

xhost +local:root

# Detect if nvidia-smi is available
if command -v nvidia-smi &> /dev/null && nvidia-smi -L &> /dev/null; then
  echo "🟢 GPU detected — enabling NVIDIA runtime"
  export DOCKER_RUNTIME=nvidia
  export GPU_DEVICES=all
else
  echo "🔵 No GPU found — falling back to CPU mode"
  export DOCKER_RUNTIME=runc
  export GPU_DEVICES=none
fi

docker compose up

docker compose down --remove-orphans