# pyright: basic

# pysme/build/tailwind.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Type, TypeVar
from copy import deepcopy

T = TypeVar("T", bound="TailwindConfig")

ThemeType = Dict[str, Any]  # Tailwind theme extensions
PluginList = List[str]  # List of plugin names


def deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries.

    :param a: The base dictionary of string keys and any values.
    :param b: The dictionary to merge in, with string keys and any values.
    :return: Merged dictionary with string keys and any values.
    """
    result: Dict[str, Any] = deepcopy(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], Dict) and isinstance(v, Dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


@dataclass
class TailwindConfig:
    content: List[str] = field(default_factory=lambda: ["**/*.pysme", "**/*.py"])
    theme: ThemeType = field(default_factory=dict)
    plugins: PluginList = field(default_factory=list)

    def merge(self, other: TailwindConfig) -> TailwindConfig:
        """
        Merge another TailwindConfig into this one.
        """
        merged_theme: ThemeType = deep_merge(self.theme, other.theme)
        merged_plugins: PluginList = list(set(self.plugins + other.plugins))
        return TailwindConfig(
            content=list(set(self.content + other.content)),
            theme=merged_theme,
            plugins=merged_plugins,
        )

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create a TailwindConfig from a dictionary."""
        return cls(
            content=list(data.get("content", [])),
            theme=dict(data.get("theme", {})),
            plugins=list(data.get("plugins", [])),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary format suitable for tailwind.config.js.
        """
        return {"content": self.content, "theme": self.theme, "plugins": self.plugins}
