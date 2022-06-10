"""Defines the AppendEntries RPC (Remote Procedure Call) as per Figure 3.1."""

from typing import Any, List

from . import BaseRPCRequest, BaseRPCResponse
from db.objects import Entry, Identity


class AppendEntriesRPCRequest(BaseRPCRequest):
  """Implements AppendEntries RPC request arguments."""

  def __init__(
    self,
    term: int,
    leader_identity: Identity,
    previous_log_index: int,
    previous_log_term: int,
    entries: List[Entry],
    leader_commit_index: int,
  ) -> None:
    # error checking
    self._validate_integer_positive(term, "term")
    self._validate_identity(leader_identity)
    self._validate_integer_positive(previous_log_index, "previous log index")
    self._validate_integer_positive(previous_log_term, "previous log term")
    self._validate_entries(entries)
    self._validate_integer_positive(leader_commit_index, "leader commit index")
    # create object by assigning read-only parameters
    self._term = term
    self._leader_identity = leader_identity
    self._previous_log_index = previous_log_index
    self._previous_log_term = previous_log_term
    self._entries = entries
    self._leader_commit_index = leader_commit_index

  @staticmethod
  def _validate_identity(obj: Any) -> None:
    """Ensure object is an indentity."""
    if not isinstance(obj, Identity):
      raise TypeError("Identity must be of 'Identity' type.")

  @staticmethod
  def _validate_entries(obj: Any) -> None:
    """Ensure object is a list of entries."""
    if not isinstance(obj, list):
      raise TypeError("`entries` must be a list.")
    elif not all(isinstance(entry, Entry) for entry in list(obj)):
      raise TypeError("Every item in `entries` must of 'Entry' type.")

  @property
  def entries(self) -> List[Entry]:
    return self._entries

  @property
  def leader_commit_index(self) -> int:
    return self._leader_commit_index

  @property
  def leader_identity(self) -> Identity:
    return self._leader_identity

  @property
  def previous_log_index(self) -> int:
    return self._previous_log_index

  @property
  def previous_log_term(self) -> int:
    return self._previous_log_term

  @property
  def term(self) -> int:
    return self._term


class AppendEntriesRPCResponse(BaseRPCResponse):
  """Implements AppendEntries RPC response results."""

  def __init__(self, term: int, success: bool) -> None:
    # error checking
    self._validate_integer_positive(term, "term")
    self._validate_boolean(success, "success")
    # create object by assigning read-only parameters
    self._term = term
    self._success = success

  @property
  def success(self):
    return self._success

  @property
  def term(self):
    return self._term
