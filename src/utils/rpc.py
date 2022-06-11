"""Defines the types of RPCs outlined in the Raft book."""

from enum import IntEnum

from typing_extensions import Literal

from .models import FrozenModel


class RPCType(IntEnum):
  # Chapter 3
  APPEND_ENTRY = 1
  REQUEST_VOTE = 2
  # Chapter 4
  ADD_SERVER = 3
  REMOVE_SERVER = 4
  # Chapter 5
  INSTALL_SNAPSHOT = 5
  # Chapter 6
  REGISTER_CLIENT = 6
  CLIENT_REQUEST = 7
  CLIENT_QUERY = 8


class RPCDirection(IntEnum):
  REQUEST = 1
  RESPONSE = 2


class RPC(FrozenModel):
  direction: Literal[
    RPCDirection.REQUEST,
    RPCDirection.RESPONSE,
  ]
  type: Literal[
    RPCType.APPEND_ENTRY,
    RPCType.REQUEST_VOTE,
    RPCType.ADD_SERVER,
    RPCType.REMOVE_SERVER,
    RPCType.INSTALL_SNAPSHOT,
    RPCType.REGISTER_CLIENT,
    RPCType.CLIENT_REQUEST,
    RPCType.CLIENT_QUERY,
  ]
  content: str
