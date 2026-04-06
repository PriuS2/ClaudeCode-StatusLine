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
    minimax_line = format_minimax_usage_line()
    if minimax_line:
        lines.append(minimax_line)
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
    """Line 2: 🧊 {percentage}% ({current}/{total}) [{bar}]"""
    context = data.get("context_window", {})
    percentage = context.get("used_percentage") or 0
    current_usage = context.get("current_usage", {})
    current = int(current_usage.get("input_tokens", 0) or 0) + int(current_usage.get("output_tokens", 0) or 0)
    total = int(context.get("context_window_size", 1) or 1)

    bar = build_progress_bar(percentage)

    return f"{EMOJI['context']} {percentage}% ({current:,}/{total:,}) [{bar}]"

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

def format_minimax_usage_line():
    """Line 4 (optional): Fetch and display MiniMax API usage"""
    import urllib.request
    import urllib.error

    settings_path = os.path.expanduser("~/.claude/settings.json")
    api_endpoint = "https://platform.minimax.io/v1/api/openplatform/coding_plan/remains"

    try:
        with open(settings_path, "r") as f:
            settings = json.load(f)
        api_key = settings.get("env", {}).get("ANTHROPIC_AUTH_TOKEN", "")
        if not api_key:
            return ""
    except Exception:
        return ""

    group_id = "2039410517440734140"
    url = f"{api_endpoint}?GroupId={group_id}"

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Referer", "https://platform.minimax.io/user-center/payment/token-plan")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            for model in data.get("model_remains", []):
                if model.get("model_name", "").startswith("MiniMax-M"):
                    five_used = model.get("current_interval_usage_count", 0)
                    five_total = model.get("current_interval_total_count", 1)
                    seven_used = model.get("current_weekly_usage_count", 0)
                    seven_total = model.get("current_weekly_total_count", 1)
                    five_end = model.get("end_time", 0)
                    seven_end = model.get("weekly_end_time", 0)

                    five_remain = max(0, five_total - five_used)
                    seven_remain = max(0, seven_total - seven_used)
                    five_pct = (five_remain / five_total * 100) if five_total > 0 else 0
                    seven_pct = (seven_remain / seven_total * 100) if seven_total > 0 else 0

                    five_bar = build_progress_bar(five_pct)
                    seven_bar = build_progress_bar(seven_pct)

                    # Calculate reset times
                    now_ms = int(time.time() * 1000)
                    five_reset = max(0, (five_end - now_ms) // 1000) if five_end else 0
                    seven_reset = max(0, (seven_end - now_ms) // 1000) if seven_end else 0

                    five_hr = five_reset // 3600
                    five_min = (five_reset % 3600) // 60
                    seven_hr = seven_reset // 3600
                    seven_min = (seven_reset % 3600) // 60

                    five_reset_str = f"{five_hr}h{five_min}m" if five_hr > 0 else f"{five_min}m"
                    seven_reset_str = f"{seven_hr}d" if seven_hr >= 24 else f"{seven_hr}h{seven_min}m"

                    return f"🌐 5h: {five_remain:,}/{five_total:,} ({five_pct:.0f}%) [{five_bar}] 7d: {seven_remain:,}/{seven_total:,} ({seven_pct:.0f}%) [{seven_bar}] (R:{five_reset_str}/{seven_reset_str})"
            return ""
    except Exception:
        return ""

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

    minimax_line = format_minimax_usage_line()
    if minimax_line:
        print(minimax_line)

if __name__ == "__main__":
    main()