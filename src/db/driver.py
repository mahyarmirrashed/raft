"""Defines the interface for appending to the log (including overwrites if
dictated to do so by the leader) and returning account balances."""

from pathlib import Path
from typing import Dict, List, Union

from pydantic import BaseModel, NonNegativeInt, StrictBool
from utils.address import Address

from . import Entry


class _Database(BaseModel):
  """Database model."""

  db: Dict[str, str]


class _Log(BaseModel):
  """Log model."""

  log: List[Entry]


class _State(BaseModel):

  current_term: NonNegativeInt
  voted_for: Union[Address, None]


relative = lambda path: Path(__file__).parent / path


class DatabaseDriver(BaseModel):
  """Driver for server variables that need to be persistent."""

  _db: _Database = _Database.parse_file(relative("json/db.json"))
  _log: _Log = _Log.parse_file(relative("json/log.json"))
  _state: _State = _State.parse_file(relative("json/state.json"))

  @classmethod
  def _dump_db(cls) -> None:
    """Store the server database to disk."""
    with open(relative("json/db.json"), mode="w") as fp:
      fp.write(cls._db.json())

  @classmethod
  def _dump_log(cls) -> None:
    """Store the server log to disk."""
    with open(relative("json/log.json"), mode="w") as fp:
      fp.write(cls._log.json())

  @classmethod
  def _dump_state(cls) -> None:
    """Store the server state to disk."""
    with open(relative("json/state.json"), mode="w") as fp:
      fp.write(cls._state.json())

  @classmethod
  def get_db(cls, key: str) -> Union[str, None]:
    """Fetch key from database."""
    return cls._db.db[key] if isinstance(key, str) else None

  @classmethod
  def get_current_term(cls) -> NonNegativeInt:
    """Fetch current term from database."""
    return cls._state.current_term

  @classmethod
  def get_voted_for(cls) -> Union[Address, None]:
    """Fetch who server voted for this term."""
    return cls._state.voted_for

  @classmethod
  def get_entry(cls, i: NonNegativeInt) -> Union[Entry, None]:
    """Fetch inside log, if it exists, else None."""
    if isinstance(i, NonNegativeInt) and 0 <= i < len(cls._log.log):
      return cls._log.log[i]
    else:
      return None

  @classmethod
  def get_log(cls) -> List[Entry]:
    """Fetch log."""
    return cls._log.log

  @classmethod
  def last_index(cls) -> NonNegativeInt:
    """Fetch index of last entry inside the log."""
    return len(cls._log.log) - 1

  @classmethod
  def set_db(cls, key: str, value: str) -> StrictBool:
    """Set key-value inside database."""
    if isinstance(key, str) and isinstance(value, str):
      cls._db.db[key] = value

      return True
    else:
      return False

  @classmethod
  def set_current_term(cls, new_term: NonNegativeInt) -> NonNegativeInt:
    """Set the current term with guarantee that new term is larger."""
    if isinstance(new_term, NonNegativeInt) and new_term > cls._state.current_term:
      cls._state.current_term = new_term
      cls._state.voted_for = None
      cls._dump_state()

    return cls._state.current_term

  @classmethod
  def set_voted_for(cls, voted_for: Union[Address, None]) -> Union[Address, None]:
    """Set who the server has voted for in this curren term."""
    if voted_for is None or isinstance(voted_for, Address):
      cls._state.voted_for = voted_for
      cls._dump_state()

    return cls._state.voted_for

  @classmethod
  def set_log(cls, new_entry: Entry) -> List[Entry]:
    """Set an entry at a given index. If valid, append, if conflicting,
    erasing everything past that entry."""
    if isinstance(new_entry, Entry) and 0 < new_entry.index <= len(cls._log.log):
      existing_entry: Union[Entry, None] = None

      if new_entry.index < len(cls._log.log):
        existing_entry = cls._log.log[new_entry.index]

      if existing_entry is None:
        cls._log.log.append(new_entry)
        cls._dump_log()
      elif new_entry.term != existing_entry.term:
        cls._log.log = cls._log.log[: new_entry.index]
        cls._log.log.append(new_entry)
        cls._dump_log()

    return cls._log.log
