#!/bin/bash
set -e

PLUGIN_NAME="claude-status-bar"
INSTALL_DIR="${HOME}/.claude/plugins/${PLUGIN_NAME}"
GITHUB_REPO="PriuS2/ClaudeCode-StatusLine"
STATUSLINE_FILE="${INSTALL_DIR}/statusline.py"

echo "Updating ${PLUGIN_NAME}..."

# Check if installed
if [ ! -d "${INSTALL_DIR}" ]; then
    echo "Error: ${PLUGIN_NAME} is not installed."
    echo "Run install.sh first."
    exit 1
fi

# Fetch latest release
LATEST_TAG=$(curl -sSL "https://api.github.com/repos/${GITHUB_REPO}/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "${LATEST_TAG}" ]; then
    echo "Error: Could not fetch latest release information."
    exit 1
fi

# Detect python3 command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# Check if update needed (compare with local file's version marker)
# For simplicity, we just always download the latest
echo "Downloading latest version..."

# Download new version
DOWNLOAD_URL="https://github.com/${GITHUB_REPO}/releases/download/${LATEST_TAG}/statusline.py"
curl -fsSL "${DOWNLOAD_URL}" -o "${STATUSLINE_FILE}"
chmod +x "${STATUSLINE_FILE}"

echo ""
echo "Update complete! Version: ${LATEST_TAG}"
echo "Restart Claude Code or start a new session."
