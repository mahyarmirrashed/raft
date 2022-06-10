"""Defines the types of RPCs outlined in the Raft book."""

from typing_extensions import Final


class RPC:
  # Chapter 3
  APPEND_ENTRY: Final[int] = 1
  REQUEST_VOTE: Final[int] = 2
  # Chapter 4
  ADD_SERVER: Final[int] = 3
  REMOVE_SERVER: Final[int] = 4
  # Chapter 5
  INSTALL_SNAPSHOT: Final[int] = 5
  # Chapter 6
  REGISTER_CLIENT: Final[int] = 6
  CLIENT_REQUEST: Final[int] = 7
  CLIENT_QUERY: Final[int] = 8
