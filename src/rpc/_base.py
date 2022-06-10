"""Defines the base RPC (Remote Procedure Call)."""

from typing import Any


class BaseRPC:
  """Implements helper methods present on all RPCs."""

  @staticmethod
  def serialize(self):
    pass

  @staticmethod
  def validate_boolean(obj: Any, name: str = "object") -> None:
    """Ensure object is boolean."""
    if not isinstance(name, str):
      raise TypeError("Object name must be a string.")
    elif not isinstance(obj, bool):
      raise TypeError(f"{name.capitalize()} must be a boolean.")

  @staticmethod
  def validate_integer(obj: Any, name: str = "object") -> None:
    """Ensure object is an integer."""
    if not isinstance(name, str):
      raise TypeError("Object name must be a string.")
    elif not isinstance(obj, int):
      raise TypeError(f"{name.capitalize()} must be an integer.")

  @staticmethod
  def validate_integer_positive(obj: Any, name: str = "object") -> None:
    """Ensure object is a positive integer."""
    BaseRPC.validate_integer(obj, name)

    if int(obj) < 0:
      raise ValueError(f"{name.capitalize()} must be greater or equal to zero.")
