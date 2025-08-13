# pyright: basic

from __future__ import annotations
import json
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, Mapping
from http import HTTPStatus
from contextlib import ContextDecorator


@dataclass
class PySmeError(Exception):
    """
    Base exception for PySme.

    Fields:
      - code: short machine code (e.g. "PSME:CFG:001")
      - message: human-friendly message
      - details: optional structured details for debugging (not user-facing)
      - hint: optional suggested remedy for user
      - cause: original exception (kept in __cause__)
      - status_code: optional HTTP mapping
      - safe: whether the message is safe to show to end-users
    """

    code: str = "PSME:GEN:000"
    message: str = "An unknown PySme error occurred"
    details: Optional[Dict[str, Any]] = field(default_factory=dict)  # type: ignore
    hint: Optional[str] = None
    cause: Optional[BaseException] = None
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    safe: bool = False

    def __post_init__(self) -> None:
        super().__init__(self.message)
        if self.cause:
            self.__cause__ = self.cause

    def __str__(self) -> str:
        return f"{self.code} - {self.message}"

    def to_dict(self, include_trace: bool = False) -> Dict[str, Any]:
        """Return a serializable dict representation. Useful for logging / HTTP responses."""
        d: Dict[str, Any] = {
            "code": self.code,
            "message": self.message if self.safe else str(self.message),
            "hint": self.hint,
            "status_code": int(self.status_code),
            "details": self.details or {},
        }
        if include_trace and self.__cause__:
            d["cause_type"] = type(self.__cause__).__name__
            d["traceback"] = traceback.format_exception(
                type(self.__cause__), self.__cause__, self.__cause__.__traceback__
            )
        return d

    def to_json(self, **kwargs) -> str:  # type: ignore
        return json.dumps(
            self.to_dict(include_trace=kwargs.pop("include_trace", False)),  # type: ignore
            default=str,
            **kwargs,  # type: ignore
        )


# ----------------------------------------------------------------------
# Subclasses
# -----------------------------------------------------------------------------------


@dataclass
class ConfigError(PySmeError):
    code: str = "PSME:CFG:001"
    message: str = "Configuration error"
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    safe: bool = False


@dataclass
class ConfigLoadError(ConfigError):
    code: str = "PSME:CFG:002"
    message: str = "Failed to load configuration file"
    hint: Optional[str] = "Check pysme.config.py for syntax errors or missing imports"
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    safe: bool = False


@dataclass
class ConfigValidationError(ConfigError):
    code: str = "PSME:CFG:003"
    message: str = "Configuration validation failed"
    details: Dict[str, Any] = field(default_factory=dict)  # type: ignore
    hint: Optional[str] = "Fix the invalid configuration fields"
    status_code: int = HTTPStatus.BAD_REQUEST
    safe: bool = True


@dataclass
class BuildError(PySmeError):
    code: str = "PSME:BLD:001"
    message: str = "Build/compile error"
    details: Dict[str, Any] = field(default_factory=dict)
    hint: Optional[str] = None
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    safe: bool = False


@dataclass
class ParserError(PySmeError):
    code: str = "PSME:PAR:001"
    message: str = "Parser error"
    details: Dict[str, Any] = field(default_factory=dict)
    hint: Optional[str] = None
    status_code: int = HTTPStatus.BAD_REQUEST
    safe: bool = True


@dataclass
class PysmeRuntimeError(PySmeError):
    code: str = "PSME:RTE:001"
    message: str = "Runtime error in component"
    details: Dict[str, Any] = field(default_factory=dict)
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    safe: bool = False


@dataclass
class NotFoundError(PySmeError):
    code: str = "PSME:API:404"
    message: str = "Not found"
    status_code: int = HTTPStatus.NOT_FOUND
    safe: bool = True


@dataclass
class AuthError(PySmeError):
    code: str = "PSME:API:401"
    message: str = "Authentication / Authorization error"
    status_code: int = HTTPStatus.UNAUTHORIZED
    safe: bool = True


@dataclass
class ValidationError(PySmeError):
    code: str = "PSME:VAL:001"
    message: str = "Validation error"
    details: Dict[str, Any] = field(default_factory=dict)
    status_code: int = HTTPStatus.BAD_REQUEST
    safe: bool = True


@dataclass
class DatabaseError(PySmeError):
    code: str = "PSME:DB:001"
    message: str = "Database error"
    details: Dict[str, Any] = field(default_factory=dict)
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    safe: bool = False


# ------------------------------------------------------
# Helpers
# -------------------------------------------------------


def exception_to_dict(
    exc: BaseException, include_trace: bool = False
) -> Dict[str, Any]:
    """
    Convert any exception into a structured dict.
    If it's a PySmeError, use to_dict(); otherwise produce a fallback shape.
    """
    if isinstance(exc, PySmeError):
        return exc.to_dict(include_trace=include_trace)

    d: Dict[str, Any] = {
        "code": "PSME:GEN:ERR",
        "message": str(exc),
        "type": type(exc).__name__,
        "safe": False,
    }

    if include_trace:
        d["traceback"] = traceback.format_exception(type(exc), exc, exc.__traceback__)
    return d


def map_exception_to_http_response(
    exc: BaseException, include_trace: bool = False
) -> Tuple[int, Mapping[str, Any]]:
    """
    Map an exception to (status_code, json_body).
    Use `safe` to decide whether to expose raw message or a generic message.
    """
    if isinstance(exc, PySmeError):
        body = exc.to_dict(include_trace=include_trace)
        status = int(exc.status_code or HTTPStatus.INTERNAL_SERVER_ERROR)
        return status, body

    body = {
        "code": "PSME:GEN:000",
        "message": "Internal server error",
        "type": type(exc).__name__,
    }
    if include_trace:
        body["traceback"] = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
    return int(HTTPStatus.INTERNAL_SERVER_ERROR), body


# -----------------------------------------------------------------
# Context management
# ------------------------------------------------------------------
class wrap_exception(ContextDecorator):
    """
    Usage:
        with wrap_exception(ConfigLoadError, message="...", details={"path": p}):
            <code that may raise>
    If the inner code raises, it will be re-raised as the specified PySmeError subclass
    using "raise ... from original".
    """

    def __init__(
        self, cls: type[PySmeError], /, message: Optional[str] = None, **kwargs: Any
    ):
        self.cls = cls
        self.message = message
        self.kwargs = kwargs

    def __enter__(self):
        return None

    def __exit__(self, exc_val, exc_type, exc_tb):
        if exc_val is None:
            return False
        if isinstance(exc_val, PySmeError):
            if self.kwargs:
                exc_val.details = {
                    **(exc_val.details or {}),
                    **self.kwargs.get("details", {}),
                }
            return False
        msg = self.message or getattr(exc_val, "message", str(exc_val))
        wrapped = self.cls(
            message=msg, details=self.kwargs.get("details", {}), cause=exc_val
        )
        raise wrapped from exc_val


# --------------------------------------
# Error factory helpers
# ---------------------------------------


def config_load_error(
    path: str, exc: Optional[BaseException] = None
) -> ConfigLoadError:
    return ConfigLoadError(
        message=f"Failed to load config at {path}", details={"path": path}, cause=exc
    )


def config_validation_error(errors: Dict[str, Any]) -> ConfigValidationError:
    return ConfigValidationError(message="Config validation failed", details=errors)
