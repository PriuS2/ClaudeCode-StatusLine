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
SPEED_CACHE_FILE = os.path.join(tempfile.gettempdir(), "statusline-speed-cache")
SPEED_HISTORY_SIZE = 5

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

def get_speed_cache():
    """Get speed cache data"""
    cache_path = Path(SPEED_CACHE_FILE)
    if cache_path.exists():
        try:
            content = cache_path.read_text().strip()
            if content:
                data = json.loads(content)
                return data.get("last_output", 0), data.get("last_api_duration", 0), data.get("last_speed", 0)
        except Exception:
            pass
    return 0, 0, 0

def save_speed_cache(last_output, last_api_duration, last_speed):
    """Save speed cache data"""
    cache_path = Path(SPEED_CACHE_FILE)
    try:
        cache_path.write_text(json.dumps({
            "last_output": last_output,
            "last_api_duration": last_api_duration,
            "last_speed": last_speed
        }))
    except Exception:
        pass

def calculate_speed(current_output, current_api_duration):
    """Calculate speed based on output token delta / api duration delta, return current speed"""
    last_output, last_api_duration, last_speed = get_speed_cache()

    if current_output > last_output and current_api_duration > last_api_duration:
        delta_output = current_output - last_output
        delta_api_duration = current_api_duration - last_api_duration  # in ms
        if delta_api_duration >= 100:  # minimum 100ms to avoid division by very small numbers
            speed = delta_output / (delta_api_duration / 1000)  # tokens per second
            save_speed_cache(current_output, current_api_duration, speed)
            return speed
    elif last_api_duration == 0:
        save_speed_cache(current_output, current_api_duration, last_speed)

    return last_speed if last_speed > 0 else None

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
    """Line 2: 🧊 {percentage}% ({current}/{total}) [{bar}] In:Xk Out:Xk ⚡Xt/s"""
    context = data.get("context_window", {})
    percentage = context.get("used_percentage") or 0
    current_usage = context.get("current_usage", {})
    input_tokens = int(current_usage.get("input_tokens", 0) or 0)
    output_tokens = int(current_usage.get("output_tokens", 0) or 0)
    current = input_tokens + output_tokens
    total = int(context.get("context_window_size", 1) or 1)

    # Get API duration for speed calculation
    total_api_duration_ms = int(data.get("cost", {}).get("total_api_duration_ms", 0) or 0)

    # Calculate speed based on output token delta / api duration delta (recent 5 average)
    current_speed = calculate_speed(output_tokens, total_api_duration_ms)
    if current_speed is not None and current_speed > 0:
        speed_str = f"⚡ {current_speed:.0f}t/s"
    else:
        speed_str = "⚡ --t/s"

    # Format tokens with k suffix for thousands
    def format_k(n):
        if n >= 1000:
            return f"{n // 1000}k"
        return str(n)

    bar = build_progress_bar(percentage)

    return f"{EMOJI['context']} {percentage}% ({current:,}/{total:,}) [{bar}] In:{format_k(input_tokens)} Out:{format_k(output_tokens)} {speed_str}"

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
                    five_used = int(model.get("current_interval_usage_count", 0) or 0)
                    five_total = int(model.get("current_interval_total_count", 1) or 1)
                    seven_used = int(model.get("current_weekly_usage_count", 0) or 0)
                    seven_total = int(model.get("current_weekly_total_count", 1) or 1)
                    five_end = int(model.get("end_time", 0) or 0)
                    seven_end = int(model.get("weekly_end_time", 0) or 0)

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
                    seven_days = seven_hr // 24
                    seven_rem_hr = seven_hr % 24
                    if seven_days > 0:
                        seven_reset_str = f"{seven_days}d{seven_rem_hr}h" if seven_rem_hr > 0 else f"{seven_days}d"
                    else:
                        seven_reset_str = f"{seven_hr}h{seven_min}m" if seven_hr > 0 else f"{seven_min}m"

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