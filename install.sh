#!/bin/bash
set -e

PLUGIN_NAME="claude-status-bar"
INSTALL_DIR="${HOME}/.claude/plugins/${PLUGIN_NAME}"
GITHUB_REPO="PriuS2/ClaudeCode-StatusLine"

echo "Installing ${PLUGIN_NAME}..."

# Detect python3 command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 not found. Please install Python 3."
    exit 1
fi

# Create install directory
mkdir -p "${INSTALL_DIR}"

# Fetch latest release version
LATEST_TAG=$(curl -sSL "https://api.github.com/repos/${GITHUB_REPO}/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "${LATEST_TAG}" ]; then
    echo "Error: Could not fetch latest release. Using main branch."
    DOWNLOAD_URL="https://raw.githubusercontent.com/${GITHUB_REPO}/main/statusline.py"
else
    echo "Latest version: ${LATEST_TAG}"
    DOWNLOAD_URL="https://github.com/${GITHUB_REPO}/releases/download/${LATEST_TAG}/statusline.py"
fi

# Download statusline.py
echo "Downloading statusline.py..."
curl -fsSL "${DOWNLOAD_URL}" -o "${INSTALL_DIR}/statusline.py"

# Make executable
chmod +x "${INSTALL_DIR}/statusline.py"

# Update settings.json
SETTINGS_FILE="${HOME}/.claude/settings.json"
PYTHON_CMD_ESCAPED=$(echo "${PYTHON_CMD}" | sed 's/\\/\\\\/g')
INSTALL_DIR_ESCAPED=$(echo "${INSTALL_DIR}" | sed 's/\\/\\\\/g')

if [ -f "${SETTINGS_FILE}" ]; then
    # Check if statusLine already exists
    if grep -q '"statusLine"' "${SETTINGS_FILE}"; then
        echo "statusLine already exists in settings.json. Skipping."
    else
        # Add statusLine to existing settings using Python for safe JSON manipulation
        python3 -c "
import json
import sys
import os
import platform

settings_path = os.path.expanduser('${SETTINGS_FILE}')
# Fix for Windows Git Bash path issue
if platform.system() == 'Windows' and settings_path.startswith('/c/'):
    settings_path = settings_path[1].upper() + ':' + settings_path[2:]
with open(settings_path, 'r') as f:
    settings = json.load(f)
settings['statusLine'] = {'type': 'command', 'command': '${PYTHON_CMD} ${INSTALL_DIR}/statusline.py'}
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
print('Updated settings.json')
"
    fi
else
    # Create new settings file
    mkdir -p "$(dirname "${SETTINGS_FILE}")"
    python3 -c "
import json
import os
import platform

settings = {'statusLine': {'type': 'command', 'command': '${PYTHON_CMD} ${INSTALL_DIR}/statusline.py'}}
settings_path = os.path.expanduser('${SETTINGS_FILE}')
# Fix for Windows Git Bash path issue
if platform.system() == 'Windows' and settings_path.startswith('/c/'):
    settings_path = settings_path[1].upper() + ':' + settings_path[2:]
os.makedirs(os.path.dirname(settings_path), exist_ok=True)
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
"
    echo "Created ${SETTINGS_FILE}"
fi

echo ""
echo "Installation complete!"
echo "Restart Claude Code or start a new session to see the status bar."