"""Defines the leader server role."""

from typing import List

from pydantic import NonNegativeInt

from . import BaseRole


class LeaderRole(BaseRole):
  """Leader role."""

  next_index: List[NonNegativeInt]
  match_index: List[NonNegativeInt]
