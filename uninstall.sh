#!/bin/bash
set -e

PLUGIN_NAME="claude-status-bar"
INSTALL_DIR="${HOME}/.claude/plugins/${PLUGIN_NAME}"
SETTINGS_FILE="${HOME}/.claude/settings.json"

echo "Uninstalling ${PLUGIN_NAME}..."

# Check if installed
if [ ! -d "${INSTALL_DIR}" ]; then
    echo "Warning: ${PLUGIN_NAME} is not installed. Nothing to do."
    exit 0
fi

# Remove plugin directory
echo "Removing ${INSTALL_DIR}..."
rm -rf "${INSTALL_DIR}"

# Remove statusLine from settings.json
if [ -f "${SETTINGS_FILE}" ]; then
    # Use python to safely remove statusLine key
    python3 -c "
import json
import sys
import os
settings_path = os.path.expanduser('${SETTINGS_FILE}')
try:
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    if 'statusLine' in settings:
        del settings['statusLine']
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        print('Removed statusLine from settings.json')
    else:
        print('statusLine not found in settings.json')
except Exception as e:
    print(f'Warning: Could not update settings.json: {e}')
"
fi

# Remove cache file if exists
CACHE_FILE="/tmp/statusline-git-cache"
if [ -f "${CACHE_FILE}" ]; then
    rm -f "${CACHE_FILE}"
    echo "Removed cache file"
fi

echo ""
echo "Uninstallation complete!"
echo "Restart Claude Code or start a new session."
