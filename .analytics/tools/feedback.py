import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_TYPES = {"gap_discovered", "improvement_applied", "known_limitation"}


def make_entry(entry_type: str, context: str, **kwargs) -> dict:
    """Build a log entry dict with a UTC timestamp.

    Args:
        entry_type: One of gap_discovered, improvement_applied, known_limitation.
        context: Human-readable description.
        **kwargs: Optional fields: severity, resolves, workaround, detail.
                  Keys with None values are excluded.

    Returns:
        Entry dict ready to pass to append_log_entry.
    """
    entry = {
        "type": entry_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": context,
    }
    entry.update({k: v for k, v in kwargs.items() if v is not None})
    return entry


def append_log_entry(entry: dict, log_path: Path) -> None:
    """Append a structured entry to the feedback log.

    Args:
        entry: Dict with at least 'type' and 'context' keys.
        log_path: Path to the JSONL log file (created if missing).

    Raises:
        TypeError: If entry is not a dict.
        ValueError: If entry type is not a valid VALID_TYPES value.
    """
    if not isinstance(entry, dict):
        raise TypeError(f"entry must be a dict, got {type(entry).__name__}")
    if entry.get("type") not in VALID_TYPES:
        raise ValueError(
            f"entry type must be one of {sorted(VALID_TYPES)}, got '{entry.get('type')}'"
        )
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Append an entry to the analytics feedback log")
    parser.add_argument("type", choices=sorted(VALID_TYPES))
    parser.add_argument("context", help="Description of the gap, improvement, or limitation")
    parser.add_argument("--detail", default=None)
    parser.add_argument("--severity", choices=["low", "medium", "high"], default=None)
    parser.add_argument("--resolves", default=None, help="Timestamp of gap_discovered this resolves")
    parser.add_argument("--workaround", default=None)
    parser.add_argument("--log-path", default=".analytics/feedback/log.jsonl")
    args = parser.parse_args()

    entry = make_entry(
        args.type,
        args.context,
        detail=args.detail,
        severity=args.severity,
        resolves=args.resolves,
        workaround=args.workaround,
    )
    append_log_entry(entry, Path(args.log_path))
    print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    main()
