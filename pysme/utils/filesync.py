# pyright: basic

from __future__ import annotations
import shutil
import tempfile
from pathlib import Path

__all__ = ("safe_write", "safe_copy")


def safe_write(target_path: str | Path, data: bytes) -> None:
    """
    Write bytes to a file atomically.
    Writes to a temp file and then renames to avoid partial writes.
    """
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        tmp_path = Path(tmp.name)

    tmp_path.replace(target)


def safe_copy(src: str | Path, dest: str | Path) -> None:
    """
    Copies a file safely (atomic replace)
    """
    src_path = Path(src)
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(dir=dest_path.parent, delete=False) as tmp:
        shutil.copyfile(src_path, tmp.name)
        tmp_path = Path(tmp.name)

    tmp_path.replace(dest_path)
