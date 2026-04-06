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
curl -sSL --connect-timeout 30 --retry 3 --retry-delay 5 -L "${DOWNLOAD_URL}" -o "${INSTALL_DIR}/statusline.py"

# Make executable
chmod +x "${INSTALL_DIR}/statusline.py"

# Update settings.json
SETTINGS_FILE="${HOME}/.claude/settings.json"

if [ -f "${SETTINGS_FILE}" ]; then
    # Check if statusLine already exists
    if grep -q '"statusLine"' "${SETTINGS_FILE}"; then
        echo "statusLine already exists in settings.json. Skipping."
    else
        # Add statusLine to existing settings using Python for safe JSON manipulation
        python3 << 'PYEOF'
import json
import sys
import os
import platform
import re

# Get HOME from environment
home = os.environ.get('HOME') or os.path.expanduser('~')

# Convert Git Bash path to Windows path
settings_path = os.path.join(home, '.claude', 'settings.json')
if platform.system() == 'Windows' and settings_path.startswith('/c/'):
    settings_path = settings_path[1].upper() + ':' + settings_path[2:]

# Read file content
with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Try parsing directly first (handles standard JSON)
try:
    settings = json.loads(content)
except json.JSONDecodeError:
    # If direct parse fails, try removing comments
    # Use a state machine approach to remove // comments outside strings
    result = []
    i = 0
    in_string = False
    while i < len(content):
        c = content[i]
        if c == '"' and (i == 0 or content[i-1] != '\\'):
            in_string = not in_string
            result.append(c)
        elif not in_string and c == '/' and i + 1 < len(content) and content[i+1] == '/':
            # Skip until end of line
            while i < len(content) and content[i] != '\n':
                i += 1
            continue
        elif not in_string and c == '/' and i + 1 < len(content) and content[i+1] == '*':
            # Skip block comment
            i += 2
            while i < len(content) - 1 and not (content[i] == '*' and content[i+1] == '/'):
                i += 1
            i += 2
            continue
        else:
            result.append(c)
        i += 1
    content = ''.join(result)
    # Remove trailing commas
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    settings = json.loads(content)

settings['statusLine'] = {'type': 'command', 'command': 'python3 ~/.claude/plugins/claude-status-bar/statusline.py'}
with open(settings_path, 'w', encoding='utf-8') as f:
    json.dump(settings, f, indent=2)
print('Updated settings.json')
PYEOF
    fi
else
    # Create new settings file
    mkdir -p "$(dirname "${SETTINGS_FILE}")"
    python3 << 'PYEOF'
import json
import os
import platform

home = os.environ.get('HOME') or os.path.expanduser('~')
settings_path = os.path.join(home, '.claude', 'settings.json')
if platform.system() == 'Windows' and settings_path.startswith('/c/'):
    settings_path = settings_path[1].upper() + ':' + settings_path[2:]

settings = {'statusLine': {'type': 'command', 'command': 'python3 ~/.claude/plugins/claude-status-bar/statusline.py'}}
os.makedirs(os.path.dirname(settings_path), exist_ok=True)
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
PYEOF
    echo "Created ${SETTINGS_FILE}"
fi

echo ""
echo "Installation complete!"
echo "Restart Claude Code or start a new session to see the status bar."