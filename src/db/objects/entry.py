"""Defines a log entry."""


class Entry:
  """Implements a log entry for the raft."""

  def __init__(self, key: str, value: int) -> None:
    # error checking
    if not isinstance(key, str):
      raise TypeError("Key must be a string.")
    elif not isinstance(value, str):
      raise TypeError("Value must be a string.")
    # create object by assigning read-only parameters
    self._key = key
    self._value = value

  @property
  def key(self) -> str:
    return self._key

  @property
  def value(self) -> int:
    return self._value
