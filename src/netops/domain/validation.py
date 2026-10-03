from __future__ import annotations

from datetime import date
from typing import Iterable
from uuid import UUID

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


def validate_uuid_text(value: str, label: str = "ID") -> str:
    normalized = str(value).strip()
    if not normalized:
        raise UserInputError(f"{label} is required.")
    try:
        UUID(normalized)
    except ValueError:
        # Existing records use uuid4().hex; accept that format too.
        try:
            UUID(hex=normalized)
        except ValueError as exc:
            raise UserInputError(f"{label} must be a UUID value.") from exc
    return normalized


def normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def normalize_required_text(value: object, label: str) -> str:
    normalized = normalize_optional_text(value)
    if normalized is None:
        raise UserInputError(f"{label} is required.")
    return normalized


def normalize_multiline_text(value: object) -> str | None:
    if value is None:
        return None
    # Preserve internal whitespace/newlines; trim only surrounding shell/form padding.
    normalized = str(value).strip()
    return normalized or None


def normalize_date_text(value: object, *, label: str = "Date", allow_month: bool = False) -> str | None:
    normalized = normalize_optional_text(value)
    if normalized is None:
        return None
    if allow_month and len(normalized) == 7:
        try:
            date.fromisoformat(f"{normalized}-01")
        except ValueError as exc:
            raise UserInputError(f"{label} must use YYYY-MM or YYYY-MM-DD format.") from exc
        return normalized
    try:
        date.fromisoformat(normalized)
    except ValueError as exc:
        raise UserInputError(f"{label} must use YYYY-MM-DD format.") from exc
    return normalized


def normalize_bool_flag(value: object) -> int:
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return 1 if value else 0
    normalized = str(value).strip().lower()
    return 1 if normalized in {"1", "true", "yes", "y", "on"} else 0


def require_entity_type(value: str, *, allowed: Iterable[str] = ("person", "interaction", "signal", "opportunity")) -> str:
    normalized = normalize_required_text(value, "Entity type").lower()
    allowed_set = set(allowed)
    if normalized not in allowed_set:
        raise UserInputError(f"Entity type must be one of: {', '.join(sorted(allowed_set))}.")
    return normalized
