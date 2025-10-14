"""Base class for special enums."""

from enum import Enum


class StrIntEnum(int, Enum):
    """Base class for enum that match string to int (vice-versa)."""

    @classmethod
    def validate(cls, value: str | int):
        """Value validator."""
        try:
            if isinstance(value, str):
                return cls[value]
            elif isinstance(value, int):
                return cls(value)
            else:
                raise ValueError(value)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error: {e}. Valid choices are: {[f'{e.name}={e.value}' for e in cls]}")
