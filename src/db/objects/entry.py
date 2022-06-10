"""Defines a log entry."""

from pydantic import BaseModel


class Entry(BaseModel):
  """Implements a log entry for the raft."""

  key: str
  value: str
