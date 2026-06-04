#!/bin/bash
set -e

echo "Running container startup configuration..."

# ALSA sound card detection
echo "Checking ALSA sound cards..."
CARD_LINE=$(aplay -l 2>/dev/null | grep -E "card [0-9]+:" | grep -i -E "analog|pch|alc|intel|realtek" | head -n 1)

if [ -z "$CARD_LINE" ]; then
    echo "🟡 No analog ALSA card found. Falling back to card 0, device 0"
    CARD_NUM=0
    DEVICE_NUM=0
else
    CARD_NUM=$(echo "$CARD_LINE" | awk '{print $2}' | tr -d ':')
    DEVICE_NUM=$(echo "$CARD_LINE" | awk -F'device ' '{print $2}' | awk '{print $1}' | tr -d ':')
    echo "🟢 Using ALSA card $CARD_NUM, device $DEVICE_NUM"
fi

# Check X11 socket(s)
if compgen -G "/tmp/.X11-unix/X*" > /dev/null; then
    echo "🟢 X11 socket(s) found:"
    ls -1 /tmp/.X11-unix/X* | xargs -n1 echo "   "
else
    echo "🟡 No X11 sockets found. GUI apps may fail."
fi

# Check PulseAudio socket
PULSE_SOCKET_PATH="${XDG_RUNTIME_DIR}/pulse/native"
if [[ -n "${PULSE_SERVER:-}" && "${PULSE_SERVER}" == unix:* ]]; then
    PULSE_SOCKET_PATH="${PULSE_SERVER#unix:}"
fi

if [[ ! -S "${PULSE_SOCKET_PATH}" ]]; then
    echo "🟡 PulseAudio socket missing. Audio via Pulse may fail."
else
    echo "🟢 PulseAudio socket is ready."
fi

echo "Container initialization complete. All systems checked."
