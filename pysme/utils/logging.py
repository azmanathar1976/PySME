from __future__ import annotations
import logging
import sys
import os
import json
from typing import Optional, Any

__all__ = ("get_logger", "configure_logging", "logger", "debug_dump")

_is_configured = False

# ---------- Formatters ----------


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        reset = self.COLORS["RESET"]
        base = super().format(record)
        return f"{color}{base}{reset}"


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_obj, ensure_ascii=False)


def configure_logging(
    level: Optional[str] = None,
    debug: Optional[bool] = None,
    json_mode: Optional[bool] = None,
) -> None:
    """
    Configure the 'pysme' top-level logger.

    Args:
        level: "DEBUG", "INFO", etc.
        debug: True -> DEBUG, False -> INFO (unless level given)
        json_mode: True -> structured logs, False -> color/text
                   (if None, uses PYSME_LOG_JSON env var)

    Environment:
        PYSME_LOG_LEVEL   ("DEBUG", "INFO", ...)
        PYSME_LOG_JSON    ("1", "true", "yes", ...)
    """
    global _is_configured

    env_level = os.getenv("PYSME_LOG_LEVEL")
    if level:
        root_level = getattr(logging, level.upper(), logging.INFO)
    elif debug is True:
        root_level = logging.DEBUG
    elif debug is False:
        root_level = logging.INFO
    elif env_level:
        root_level = getattr(logging, env_level.upper(), logging.INFO)
    else:
        root_level = logging.INFO

    if json_mode is None:
        env_json = os.getenv("PYSME_LOG_JSON", "").strip().lower()
        if env_json in ("1", "true", "yes", "on"):
            json_mode = True
        elif env_json in ("0", "false", "no", "off"):
            json_mode = False
        else:
            json_mode = False  # default to human-friendly

    if json_mode:
        formatter = JSONFormatter()
    else:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = ColorFormatter(fmt=fmt, datefmt=datefmt)

    log = logging.getLogger("pysme")
    log.setLevel(root_level)
    log.propagate = False

    if not _is_configured:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        log.addHandler(handler)
        _is_configured = True
    else:
        # Reconfigure all handlers in-place
        for h in log.handlers:
            h.setFormatter(formatter)
        log.setLevel(root_level)


def get_logger(name: str = "pysme") -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)


logger = get_logger()


def debug_dump(obj: Any, label: str = "DEBUG DUMP") -> None:
    import pprint

    logger.debug("%s:\n%s", label, pprint.pformat(obj))
