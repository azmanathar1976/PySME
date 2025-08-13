from __future__ import annotations
import json
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from http import HTTPStatus


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
