import json
from pathlib import Path

import pytest

from feedback import append_log_entry, make_entry, VALID_TYPES


def test_gap_discovered_written(tmp_path):
    log_path = tmp_path / "log.jsonl"
    entry = make_entry("gap_discovered", "user asked for geospatial map", severity="high")
    append_log_entry(entry, log_path)
    saved = json.loads(log_path.read_text().strip())
    assert saved["type"] == "gap_discovered"
    assert saved["context"] == "user asked for geospatial map"
    assert saved["severity"] == "high"
    assert "timestamp" in saved


def test_improvement_applied_written(tmp_path):
    log_path = tmp_path / "log.jsonl"
    entry = make_entry("improvement_applied", "added box plot support to viz.py")
    append_log_entry(entry, log_path)
    saved = json.loads(log_path.read_text().strip())
    assert saved["type"] == "improvement_applied"


def test_known_limitation_written_with_workaround(tmp_path):
    log_path = tmp_path / "log.jsonl"
    entry = make_entry("known_limitation", "PDF export not supported", workaround="print to PDF from browser")
    append_log_entry(entry, log_path)
    saved = json.loads(log_path.read_text().strip())
    assert saved["type"] == "known_limitation"
    assert saved["workaround"] == "print to PDF from browser"


def test_multiple_entries_append_not_overwrite(tmp_path):
    log_path = tmp_path / "log.jsonl"
    for i in range(3):
        append_log_entry(make_entry("gap_discovered", f"gap {i}"), log_path)
    lines = log_path.read_text().strip().split("\n")
    assert len(lines) == 3


def test_creates_parent_directories(tmp_path):
    log_path = tmp_path / "nested" / "dir" / "log.jsonl"
    append_log_entry(make_entry("gap_discovered", "test"), log_path)
    assert log_path.exists()


def test_invalid_entry_type_raises(tmp_path):
    log_path = tmp_path / "log.jsonl"
    with pytest.raises(ValueError, match="gap_discovered"):
        append_log_entry({"type": "unknown_type", "context": "test"}, log_path)


def test_entry_not_dict_raises(tmp_path):
    log_path = tmp_path / "log.jsonl"
    with pytest.raises(TypeError, match="dict"):
        append_log_entry("not a dict", log_path)


def test_none_kwargs_excluded_from_entry():
    entry = make_entry("gap_discovered", "test", severity=None, resolves=None)
    assert "severity" not in entry
    assert "resolves" not in entry
