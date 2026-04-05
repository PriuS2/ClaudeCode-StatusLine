#!/usr/bin/env python3
"""Claude Code Status Line
Displays: directory, branch, model, context usage, cost, rate limits
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Fix Windows console encoding for emoji output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CACHE_FILE = os.path.join(tempfile.gettempdir(), "statusline-git-cache")
CACHE_MAX_AGE = 5  # seconds

EMOJI = {
    "directory": "📁",
    "branch": "🌿",
    "model": "🧠",
    "context": "🧊",
    "cost": "💰",
    "timer": "⏱️",
    "rate": "⏳",
}

PROGRESS_FULL = "█"
PROGRESS_EMPTY = "░"

def get_cached_git_info():
    """Get git info from cache or fresh fetch"""
    cache_path = Path(CACHE_FILE)

    if cache_path.exists():
        age = time.time() - cache_path.stat().st_mtime
        if age < CACHE_MAX_AGE:
            content = cache_path.read_text().strip()
            if content:
                parts = content.split("|")
                if len(parts) == 3:
                    return parts[0], parts[1], parts[2]

    # Fresh fetch
    branch, staged, modified = "", "0", "0"
    try:
        subprocess.run(["git", "rev-parse", "--git-dir"],
                      capture_output=True, check=True, timeout=2)
        branch = subprocess.run(["git", "branch", "--show-current"],
                               capture_output=True, text=True, timeout=2).stdout.strip()
        staged = subprocess.run(["git", "diff", "--cached", "--numstat"],
                               capture_output=True, text=True, timeout=2).stdout.strip()
        modified = subprocess.run(["git", "diff", "--numstat"],
                                  capture_output=True, text=True, timeout=2).stdout.strip()
        staged = str(len([l for l in staged.split("\n") if l.strip()]))
        modified = str(len([l for l in modified.split("\n") if l.strip()]))
    except Exception:
        branch = ""

    # Write cache
    try:
        cache_path.write_text(f"{branch}|{staged}|{modified}")
    except Exception:
        pass

    return branch, staged, modified

def build_progress_bar(percentage, width=10):
    """Build a text progress bar"""
    filled = int(percentage * width / 100)
    empty = width - filled
    return PROGRESS_FULL * filled + PROGRESS_EMPTY * empty

def parse_json_input():
    """Parse JSON from stdin"""
    try:
        return json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return None

def parse_json(input_str):
    """Parse JSON from string input"""
    try:
        return json.loads(input_str)
    except json.JSONDecodeError:
        return None

def format_output(data):
    """Format data for status line output - returns list of 3 lines"""
    lines = []
    lines.append(format_workspace_line(data))
    lines.append(format_context_line(data))
    rate_line = format_rate_limits_line(data)
    if rate_line:
        lines.append(rate_line)
    return lines

def format_workspace_line(data):
    """Line 1: 📁 {dir} 🌿 {branch} 🧠 {model}"""
    directory = os.path.basename(data.get("workspace", {}).get("current_dir") or data.get("cwd") or "")
    model = data.get("model", {}).get("display_name") or "Unknown"

    branch, staged, modified = get_cached_git_info()

    line = f"{EMOJI['directory']} {directory} "
    if branch:
        line += f"{EMOJI['branch']} {branch} "
    line += f"{EMOJI['model']} {model}"
    return line

def format_context_line(data):
    """Line 2: 🧊 {percentage}% [{bar}] 💰 ${cost} (${cost_per_hour}/h)"""
    context = data.get("context_window", {})
    percentage = context.get("used_percentage") or 0
    cost = data.get("cost", {}).get("total_cost_usd") or 0

    bar = build_progress_bar(percentage)
    cost_str = f"${cost:.2f}"

    # Estimate cost per hour
    duration_ms = data.get("cost", {}).get("total_duration_ms") or 1
    hours = duration_ms / 3600000
    cost_per_hour = cost / hours if hours > 0 else 0
    cost_per_hour_str = f"${cost_per_hour:.2f}/h"

    return f"{EMOJI['context']} {percentage}% [{bar}] {EMOJI['cost']} {cost_str} ({cost_per_hour_str})"

def format_rate_limits_line(data):
    """Line 3: ⏳ 5h: {percentage}% [{bar}] 7d: {percentage}% [{bar}]"""
    rate_limits = data.get("rate_limits")

    if not rate_limits:
        return ""

    parts = []
    for window in ["five_hour", "seven_day"]:
        window_data = rate_limits.get(window)
        if window_data:
            percentage = window_data.get("used_percentage") or 0
            bar = build_progress_bar(percentage)
            label = "5h" if window == "five_hour" else "7d"
            parts.append(f"{label}: {percentage:.0f}% [{bar}]")

    if not parts:
        return ""

    return f"{EMOJI['rate']} " + " ".join(parts)

def main():
    data = parse_json_input()
    if not data:
        print("Error: Invalid JSON input")
        return

    print(format_workspace_line(data))
    print(format_context_line(data))

    rate_line = format_rate_limits_line(data)
    if rate_line:
        print(rate_line)

if __name__ == "__main__":
    main()