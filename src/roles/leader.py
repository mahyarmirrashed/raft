"""Defines the leader server role."""

from typing import Dict

from pydantic import NonNegativeInt

from . import BaseRole
from utils import Address


class LeaderRole(BaseRole):
  """Leader role."""

  next_index: Dict[Address, NonNegativeInt]
  match_index: Dict[Address, NonNegativeInt]
