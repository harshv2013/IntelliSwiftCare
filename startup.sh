#!/bin/bash
set -euo pipefail

# Default port Azure provides; fallback to 8501 for local testing
: "${PORT:=8000}"

# Where we'll put the venv (must be inside /home so it persists across runs)
VENV_DIR="/home/site/wwwroot/antenv"

echo "==== startup.sh begins ===="
echo "PORT=$PORT"
date

# Choose python binary available in the container
PYTHON_BIN=$(which python3 || which python || /usr/bin/python3)
echo "Using python: $PYTHON_BIN"

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv at $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  echo "Virtualenv already exists at $VENV_DIR"
fi

PIP_BIN="$VENV_DIR/bin/pip"
PY_BIN="$VENV_DIR/bin/python"

# Upgrade pip in the venv (safe)
echo "Upgrading pip in venv..."
"$PY_BIN" -m pip install --upgrade pip setuptools wheel --no-cache-dir

# Install requirements if requirements.txt exists and dependencies not installed
if [ -f "/home/site/wwwroot/requirements.txt" ]; then
  echo "Installing requirements from /home/site/wwwroot/requirements.txt"
  "$PIP_BIN" install --no-cache-dir -r /home/site/wwwroot/requirements.txt
else
  echo "No requirements.txt found in /home/site/wwwroot — skipping pip install"
fi

# Streamlit environment (headless)
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLECORS=false
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_LOG_LEVEL=info

echo "Starting Streamlit with: $PY_BIN -m streamlit run /home/site/wwwroot/app.py --server.port $PORT --server.address 0.0.0.0"
date
exec "$PY_BIN" -m streamlit run /home/site/wwwroot/app.py --server.port "$PORT" --server.address "0.0.0.0"
