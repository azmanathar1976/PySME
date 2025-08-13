from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any

VALID_OPT_LEVELS = {"release", "debug"}


@dataclass
class BuildConfig:
    """
    Defines build config for building apps for production.
    """

    entry_point: str = "pages/index.component.pysme"
    output_dir: str = "dist"
    static_dir: str = "static"
    wasm_target: str = "web"
    optimization_level: str = "release"
    bundle_splitting: bool = False
    tree_shaking: bool = False

    def __post_init__(self) -> None:
        if self.optimization_level not in VALID_OPT_LEVELS:
            raise ValueError(
                f"Invalid optimization_level={self.optimization_level!r}. "
                f"Valid values: {VALID_OPT_LEVELS}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BuildConfig":
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in allowed}
        return cls(**filtered)
