"""Defines a log entry."""

from pydantic import BaseModel, StrictStr


class Entry(BaseModel):
  """Implements a log entry for the raft."""

  key: StrictStr
  value: StrictStr
