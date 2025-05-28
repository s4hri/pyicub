#!/bin/bash
set -e

echo "Running host pre-launch configuration..."

# Ensure PulseAudio is running
if ! pactl info > /dev/null 2>&1; then
    echo "🟡 PulseAudio not running. Trying to start it..."
    pulseaudio --start || echo "[ERROR] Failed to start PulseAudio."
fi

# Grant X11 access
if command -v xhost &> /dev/null; then
    xhost +local:docker > /dev/null
    echo "🟢 X11 access granted to Docker containers."
else
    echo "🟡 'xhost' not found. GUI apps may not display correctly."
fi

# Check Pulse socket
PULSE_SOCKET="$XDG_RUNTIME_DIR/pulse/native"
if [[ ! -S "$PULSE_SOCKET" ]]; then
    echo "🟡 PulseAudio socket not found at $PULSE_SOCKET"
else
    echo "🟢 PulseAudio socket found: $PULSE_SOCKET"
fi

# Detect GPU availability
if command -v nvidia-smi &> /dev/null && nvidia-smi -L &> /dev/null; then
  echo "🟢 GPU detected — enabling NVIDIA runtime"
  export DOCKER_RUNTIME=nvidia
  export GPU_DEVICES=all
else
  echo "🔵 No GPU found — falling back to CPU mode"
  export DOCKER_RUNTIME=runc
  export GPU_DEVICES=none
fi

# SSH Agent detection and sharing
if [[ -S "$SSH_AUTH_SOCK" ]]; then
    echo "🟢 SSH agent detected at $SSH_AUTH_SOCK"
    export SSH_AUTH_SOCK
else
    echo "🟡 SSH agent not running. Please start it and add your keys (ssh-agent / ssh-add)."
    echo "    Example: eval \$(ssh-agent) && ssh-add ~/.ssh/id_rsa"
fi

echo "Host setup successful. Ready to launch Docker containers."
