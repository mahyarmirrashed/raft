"""Defines the base server role."""

from typing import List, Union

from db import Entry, DatabaseDriver
from pydantic import BaseModel, NonNegativeInt
from utils import Address


class BaseRole(BaseModel):
  """Implements state properties present on all servers."""

  _driver: DatabaseDriver = DatabaseDriver()
  current_term: NonNegativeInt = _driver.get_current_term()
  voted_for: Union[Address, None] = _driver.get_voted_for()
  log: List[Entry] = _driver.get_log()
  commit_index: NonNegativeInt
  last_applied_index: NonNegativeInt

  @classmethod
  def apply_commits(cls) -> None:
    """Apply all committed entries to the state machine."""
    while cls.commit_index > cls.last_applied_index:
      entry = cls.log[cls.last_applied_index]
      cls._driver.update_db(entry.key, entry.value)
      cls.last_applied_index += 1

  @classmethod
  def update_current_term(cls, new_term: NonNegativeInt) -> None:
    """Update the current term with the driver, then here."""
    cls.current_term = cls._driver.update_current_term(new_term)

  @classmethod
  def update_voted_for(cls, voted_for: Union[Address, None]) -> None:
    """Update the voted for first with the driver, then here."""
    cls.voted_for = cls._driver.update_voted_for(voted_for)

  @classmethod
  def update_log(cls, new_entry: Entry) -> None:
    """Update the log first with the driver, then here."""
    cls.log = cls._driver.update_log(new_entry)
