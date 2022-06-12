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

  def apply_commits(self) -> None:
    """Apply all committed entries to the state machine."""
    while self.commit_index > self.last_applied_index:
      entry = self.log[self.last_applied_index]
      print(f"INFO: Applying {entry} to the database.")

      self._driver.set_db(entry.key, entry.value)
      self.last_applied_index += 1

  def update_current_term(self, new_term: NonNegativeInt) -> None:
    """Update the current term with the driver, then here."""
    self.current_term = self._driver.set_current_term(new_term)

  def update_voted_for(self, voted_for: Union[Address, None]) -> None:
    """Update the voted for first with the driver, then here."""
    print(f"INFO: Voted {voted_for} for term {self.current_term}.")
    self.voted_for = self._driver.set_voted_for(voted_for)

  def update_log(self, new_entry: Entry) -> None:
    """Update the log first with the driver, then here."""
    self.log = self._driver.set_log(new_entry)
