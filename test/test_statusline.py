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