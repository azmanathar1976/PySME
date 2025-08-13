# pyright: basic

from __future__ import annotations
from pathlib import Path

__all__ = ("resolve_path", "project_root", "ensure_dir")


def project_root() -> Path:
    """
    Return the root directory of the project (where .git or pyproject.toml is found).
    Falls back to current working directory.
    """
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return cwd


def resolve_path(path: str | Path, base: Path | None = None) -> Path:
    """
    Resolve a given path to an absolute path.
    If relative, join with base or project root.
    """
    p = Path(path)
    if not p.is_absolute():
        p = (base or project_root()) / p
    return p.resolve()


def ensure_dir(path: str | Path) -> Path:
    """
    Ensure that a directory exists, create if missing.
    Returns the Path object.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
