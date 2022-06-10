"""Defines a server identity."""

import re

from pydantic import BaseModel, ConstrainedStr, validator
from typing_extensions import Final

LENGTH: Final[int] = 64


class _Sha256Hash(ConstrainedStr):
  strip_whitespace = True
  to_lower = True
  min_length = LENGTH
  max_length = LENGTH
  regex = re.compile(r"^[0-9A-F]+$")


class Identity(BaseModel):
  """Implements controlled method for building and transferring server identities."""

  value: _Sha256Hash
