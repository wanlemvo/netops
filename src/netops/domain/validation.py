from __future__ import annotations

from datetime import date
from typing import Iterable

from pydantic import ValidationError


class NetOpsError(Exception):
    """Base exception with a user-facing message."""


class NotFoundError(NetOpsError):
    pass


class AmbiguousMatchError(NetOpsError):
    pass


class UserInputError(NetOpsError):
    pass


def format_validation_error(error: ValidationError | ValueError) -> str:
    if isinstance(error, ValidationError):
        parts = []
        for item in error.errors():
            location = ".".join(str(part) for part in item["loc"])
            parts.append(f"{location}: {item['msg']}")
        return "; ".join(parts)
    return str(error)


def require_not_future(value: date, *, allow_future: bool = False) -> None:
    if value > date.today() and not allow_future:
        raise UserInputError("The date is in the future. Re-run with confirmation or choose another date.")


def require_choice(value: str, choices: Iterable[str], label: str) -> str:
    normalized = value.strip().lower()
    if normalized not in set(choices):
        raise UserInputError(f"{label} must be one of: {', '.join(choices)}.")
    return normalized


def normalize_text_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


def normalize_relationship_strength(value: str | int | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    allowed = {"1", "2", "3", "4", "5", "low", "medium", "high"}
    if normalized not in allowed:
        raise UserInputError("Relationship strength must be 1-5, low, medium, or high.")
    return normalized
