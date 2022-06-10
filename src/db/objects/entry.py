"""Defines a log entry."""

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
  """Implements a log entry for the raft."""

  key: str
  value: str
