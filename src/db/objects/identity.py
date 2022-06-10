"""Defines a server identity."""

from string import hexdigits

from pydantic import validator
from pydantic.dataclasses import dataclass
from typing_extensions import Final

LENGTH: Final[int] = 64


@dataclass(frozen=True)
class Identity:
  """Implements controlled method for building and transferring server identities."""

  value: str

  @validator("value")
  def check_hexadecimal(cls, v):
    assert set(v).issubset(set(hexdigits)), f"{v} must be hexadecimal"
    return v

  @validator("value")
  def check_length(cls, v):
    assert len(v) == LENGTH, f"value must be {LENGTH} characters"
    return v
