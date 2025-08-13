# pyright: reportUnknownVariableType=false

from __future__ import annotations
import importlib.util
import sys
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, Optional
import json

from .utils.logging import logger, configure_logging
from .build.config import BuildConfig
from .build.tailwind import TailwindConfig

DEFAULT_CONFIG_FILENAME = "pysme.config.py"
_MODULE_NAME = "pysme_user_config"


@dataclass
class LoadedConfigs:
    build: BuildConfig
    tailwind: TailwindConfig
    raw: Dict[str, Any] | None = None


def _bool_from_env(v: Optional[str]) -> Optional[bool]:
    if v is None:
        return None

    v = v.strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return None


def _list_from_env(v: Optional[str]) -> Optional[list[str]]:
    if not v:
        return None
    return [s.strip() for s in v.split(",") if s.strip()]


def _json_from_env(v: Optional[str]) -> Optional[dict]:  # type: ignore
    if not v:
        return None
    try:
        return json.loads(v)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in env var: %r", v)
        return None


def _apply_env_overrides(build: BuildConfig, tailwind: TailwindConfig) -> None:
    # Common overrides
    if v := os.getenv("PYSME_ENTRY_POINT"):
        build.entry_point = v
    if v := os.getenv("PYSME_OUTPUT_DIR"):
        build.output_dir = v
    if v := os.getenv("PYSME_STATIC_DIR"):
        build.static_dir = v
    if v := os.getenv("PYSME_WASM_TARGET"):
        build.wasm_target = v
    if v := os.getenv("PYSME_OPT_LEVEL"):
        build.optimization_level = v
    if v := os.getenv("PYSME_BUNDLE_SPLITTING"):
        b = _bool_from_env(v)
        if b is not None:
            build.bundle_splitting = b
    if v := os.getenv("PYSME_TREE_SHAKING"):
        b = _bool_from_env(v)
        if b is not None:
            build.tree_shaking = b

    if v := os.getenv("PYSME_TAILWIND_CONTENT"):
        content_list = _list_from_env(v)
        if content_list is not None:
            tailwind.content = content_list
    if v := os.getenv("PYSME_TAILWIND_THEME"):
        theme_obj = _json_from_env(v)
        if theme_obj is not None:
            tailwind.theme = theme_obj
    if v := os.getenv("PYSME_TAILWIND_PLUGINS"):
        plugins_list = _list_from_env(v)
        if plugins_list is not None:
            tailwind.plugins = plugins_list


def _make_defaults() -> LoadedConfigs:
    return LoadedConfigs(build=BuildConfig(), tailwind=TailwindConfig(), raw={})


def load_pysme_config(
    config_path: str = DEFAULT_CONFIG_FILENAME, apply_env: bool = True
) -> LoadedConfigs:
    """
    Load user config file (python file) and return typed objects.
    If file does not exist, return defaults.
    The user file may set:
      - build_config (BuildConfig instance or dict)
      - tailwind_config (TailwindConfig instance or dict)
      - debug (bool) — will be applied to logging if present
      - other top-level variables (collected into raw)
    """
    path = Path(config_path)
    if not path.exists():
        logger.info("No %s found, using default config", config_path)
        cfgs = _make_defaults()
        if apply_env:
            _apply_env_overrides(cfgs.build, cfgs.tailwind)
        # Configure env based on env only
        configure_logging()
        return cfgs

    # Unload previous module if present so reload works
    if _MODULE_NAME in sys.modules:
        del sys.modules[_MODULE_NAME]

    spec = importlib.util.spec_from_file_location(_MODULE_NAME, str(path))
    if not spec or spec.loader is None:
        logger.error("Failed to create import spec for %s", path)
        return _make_defaults()

    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        logger.error("Error executing config file %s: %s", path, exc, exc_info=True)
        return _make_defaults()

    raw_vars = {k: v for k, v in vars(module).items() if not k.startswith("_")}

    # build config
    bc = getattr(module, "build_config", None)
    if isinstance(bc, BuildConfig):
        build_conf = bc
    elif isinstance(bc, dict):
        build_conf = BuildConfig.from_dict(bc)  # type:ignore
    elif bc is None:
        build_conf = BuildConfig()
    else:
        raise TypeError("build_config in pysme.config.py must be BuildConfig or dict")

    tc = getattr(module, "tailwind_config", None)
    if isinstance(tc, TailwindConfig):
        tailwind_conf = tc
    elif isinstance(tc, dict):
        tailwind_conf = TailwindConfig.from_dict(tc)  # type:ignore
    elif tc is None:
        tailwind_conf = TailwindConfig()
    else:
        raise TypeError(
            "tailwind_config in pysme.config.py must be TailwindConfig or dict"
        )

    if apply_env:
        _apply_env_overrides(build_conf, tailwind_conf)

    debug_flag = getattr(module, "debug", None)
    if debug_flag is None:
        env_debug = _bool_from_env(os.getenv("PYSME_DEBUG"))
        if env_debug is not None:
            debug_flag = env_debug

    try:
        configure_logging(debug=bool(debug_flag) if debug_flag is not None else None)
    except Exception:
        configure_logging()

    logger.info("Loaded config from %s", path)
    return LoadedConfigs(build=build_conf, tailwind=tailwind_conf, raw=raw_vars)


def reload_pysme_config(
    config_path: str = DEFAULT_CONFIG_FILENAME, apply_env: bool = True
) -> LoadedConfigs:
    return load_pysme_config(config_path=config_path, apply_env=apply_env)
