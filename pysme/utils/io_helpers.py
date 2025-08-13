# pyright: basic

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

__all__ = ("read_json", "write_json", "read_yaml", "write_yaml")


def read_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, data: Any, *, indent: int = 4) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_yaml(path: str | Path) -> Any:
    if yaml is None:
        raise RuntimeError("PyYAML is not installed. Run `pip install pyyaml`.")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: str | Path, data: Any) -> None:
    if yaml is None:
        raise RuntimeError("PyYAML is not installed. Run `pip install pyyaml`.")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)
