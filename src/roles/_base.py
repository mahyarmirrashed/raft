"""Defines the base server role."""

from typing import List

from db.objects.entry import Entry
from db.objects.identity import Identity
from pydantic import BaseModel, NonNegativeInt


class BaseRole(BaseModel):
  """Implements state properties present on all servers."""

  current_term: NonNegativeInt
  voted_for: Identity
  log: List[Entry]
  commit_index: NonNegativeInt
  last_applied_index: NonNegativeInt
