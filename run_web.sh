#!/usr/bin/env bash
# Launch headless audio analysis + web receiver.
#
# Usage:
#   ./run_web.sh                       # use device from config.yaml
#   ./run_web.sh --device HK-MIC1      # override microphone
#   ./run_web.sh --list-devices        # just list mics and exit
#
# The web UI will be available at: http://localhost:3000
# Press Ctrl+C to stop both processes.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate conda env if available
if command -v conda &>/dev/null; then
    eval "$(conda shell.bash hook)"
    conda activate ML311
fi

# If user just wants to list devices, do that and exit
for arg in "$@"; do
    if [[ "$arg" == "--list-devices" ]]; then
        python audio_analysis_background.py --list-devices
        exit 0
    fi
done

# Make sure receiver deps are installed
if [ ! -d "receiver/node_modules" ]; then
    echo "[setup] installing receiver npm deps..."
    (cd receiver && npm install)
fi

# Track child PIDs for clean shutdown
PIDS=()
cleanup() {
    echo ""
    echo "[shutdown] stopping background processes..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null
    done
    wait 2>/dev/null
    exit 0
}
trap cleanup INT TERM

# 1) Start the web receiver (OSC → WebSocket bridge + HTTP server)
echo "[launch] starting web receiver on http://localhost:3000 ..."
(cd receiver && npm start) &
PIDS+=($!)

# Give the bridge a moment to bind its UDP port
sleep 1

# 2) Start the headless audio analysis (forwards all CLI args)
echo "[launch] starting audio analysis (headless) ..."
python audio_analysis_background.py "$@" &
PIDS+=($!)

echo ""
echo "  Open: http://localhost:3000"
echo "  Ctrl+C to stop."
echo ""

wait
