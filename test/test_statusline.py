#!/usr/bin/env python3
"""Tests for statusline.py"""
import json
import subprocess
import sys
from io import StringIO

# Mock JSON data matching Claude Code's statusline input format
MOCK_INPUT = {
    "cwd": "/Users/test/project",
    "session_id": "abc123",
    "model": {"id": "claude-opus-4-6", "display_name": "Opus"},
    "workspace": {"current_dir": "/Users/test/project", "project_dir": "/Users/test", "added_dirs": []},
    "version": "2.1.90",
    "cost": {"total_cost_usd": 1.25, "total_duration_ms": 3600000, "total_api_duration_ms": 5000, "total_lines_added": 100, "total_lines_removed": 20},
    "context_window": {"total_input_tokens": 10000, "total_output_tokens": 5000, "context_window_size": 200000, "used_percentage": 5, "remaining_percentage": 95, "current_usage": {"input_tokens": 10000, "output_tokens": 5000, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}},
    "rate_limits": {"five_hour": {"used_percentage": 21.5, "resets_at": 1738425600}, "seven_day": {"used_percentage": 44.2, "resets_at": 1738857600}}
}

def test_import_statusline():
    """statusline.py can be imported without error"""
    import statusline
    assert hasattr(statusline, 'parse_json'), "parse_json function exists"
    assert hasattr(statusline, 'format_output'), "format_output function exists"

def test_parse_json_valid():
    """parse_json correctly parses valid input"""
    import statusline
    result = statusline.parse_json(json.dumps(MOCK_INPUT))
    assert result['model']['display_name'] == 'Opus'
    assert result['context_window']['used_percentage'] == 5

def test_parse_json_invalid():
    """parse_json handles invalid JSON gracefully"""
    import statusline
    result = statusline.parse_json("not valid json")
    assert result is None

def test_run_with_mock_input():
    """statusline.py produces output when run with mock input"""
    result = subprocess.run(
        [sys.executable, 'statusline.py'],
        input=json.dumps(MOCK_INPUT),
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    lines = result.stdout.strip().split('\n')
    assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
    assert 'Opus' in lines[0]

def test_build_progress_bar_zero():
    """build_progress_bar handles 0% correctly"""
    import statusline
    bar = statusline.build_progress_bar(0)
    assert bar == "░░░░░░░░░░"

def test_build_progress_bar_full():
    """build_progress_bar handles 100% correctly"""
    import statusline
    bar = statusline.build_progress_bar(100)
    assert bar == "██████████"

def test_format_rate_limits_empty():
    """format_rate_limits_line returns empty string when rate_limits is None"""
    import statusline
    result = statusline.format_rate_limits_line({})
    assert result == ""

def test_format_rate_limits_absent():
    """format_rate_limits_line returns empty string when rate_limits is absent"""
    import statusline
    result = statusline.format_rate_limits_line({})
    assert result == ""

def test_format_speed_suffix_no_cache():
    """format_speed_suffix returns --t/s when no cache exists"""
    import statusline
    import tempfile
    import os

    # Clear any existing cache
    cache_path = os.path.join(tempfile.gettempdir(), "statusline-speed-cache")
    if os.path.exists(cache_path):
        os.remove(cache_path)

    data = {
        "context_window": {
            "total_output_tokens": 1000,
            "current_usage": {"output_tokens": 100}
        },
        "cost": {"total_api_duration_ms": 0}
    }
    result = statusline.format_speed_suffix(data)
    assert "⚡--" in result and "Avg:--" in result


def test_format_speed_suffix_with_calculation():
    """format_speed_suffix calculates speed from data"""
    import statusline
    import tempfile
    import os
    import time

    # Pre-populate cache with recent data
    cache_path = os.path.join(tempfile.gettempdir(), "statusline-speed-cache")
    recent_timestamp = int(time.time() * 1000) - 1000  # 1 second ago
    with open(cache_path, 'w') as f:
        f.write(f"500|{recent_timestamp}|50")

    data = {
        "context_window": {
            "total_output_tokens": 1000,
            "current_usage": {"output_tokens": 100}
        },
        "cost": {"total_api_duration_ms": 100000}  # 100 seconds
    }
    result = statusline.format_speed_suffix(data)
    # total_output_tokens=1000, api_duration=100s, so avg=10 t/s
    # Delta = 500 tokens over ~1 seconds = ~500 t/s current
    assert "Avg:10t/s" in result
    assert "⚡" in result


def test_calculate_speed_divide_by_zero():
    """calculate_speed handles zero api_duration_ms"""
    import statusline
    import tempfile
    import os

    # Clear cache
    cache_path = os.path.join(tempfile.gettempdir(), "statusline-speed-cache")
    if os.path.exists(cache_path):
        os.remove(cache_path)

    data = {
        "context_window": {
            "total_output_tokens": 1000,
            "current_usage": {"output_tokens": 100}
        },
        "cost": {"total_api_duration_ms": 0}
    }
    current_speed, avg_speed = statusline.calculate_speed(data)
    assert avg_speed is None  # Cannot calculate with 0 duration


def test_calculate_speed_cache_stale():
    """calculate_speed returns None current_speed when no cache exists"""
    import statusline
    import tempfile
    import os

    # Clear cache to simulate no previous data
    cache_path = os.path.join(tempfile.gettempdir(), "statusline-speed-cache")
    if os.path.exists(cache_path):
        os.remove(cache_path)

    data = {
        "context_window": {
            "total_output_tokens": 1000,
            "current_usage": {"output_tokens": 100}
        },
        "cost": {"total_api_duration_ms": 100000}
    }
    current_speed, avg_speed = statusline.calculate_speed(data)
    assert current_speed is None  # No cache, cannot calculate current speed
    assert avg_speed is not None  # Average still calculable: 1000/100 = 10 t/s


def test_format_context_line_with_speed():
    """format_context_line includes speed suffix"""
    import statusline
    import tempfile
    import os

    # Clear cache
    cache_path = os.path.join(tempfile.gettempdir(), "statusline-speed-cache")
    if os.path.exists(cache_path):
        os.remove(cache_path)

    data = {
        "context_window": {
            "used_percentage": 35,
            "context_window_size": 200000,
            "current_usage": {"input_tokens": 45000, "output_tokens": 3000},
            "total_output_tokens": 3000
        },
        "cost": {"total_api_duration_ms": 250000}  # 250 seconds
    }
    result = statusline.format_context_line(data)
    assert "⚡--" in result  # No previous cache, current speed unknown
    assert "Avg:12t/s" in result  # 3000 tokens / 250 seconds = 12 t/s