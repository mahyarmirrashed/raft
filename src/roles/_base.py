"""Defines the base server role."""

from typing import List

from db import Entry
from pydantic import BaseModel, NonNegativeInt
from utils import Address


class BaseRole(BaseModel):
  """Implements state properties present on all servers."""

  current_term: NonNegativeInt
  voted_for: Address
  log: List[Entry]
  commit_index: NonNegativeInt
  last_applied_index: NonNegativeInt
