"""Defines a log entry."""

from pydantic import BaseModel, NonNegativeInt, StrictStr


class Entry(BaseModel):
  """Implements a log entry for the raft."""

  index: NonNegativeInt
  term: NonNegativeInt
  key: StrictStr
  value: StrictStr
