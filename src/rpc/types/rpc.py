"""Defines the types of RPCs outlined in the Raft book."""


class RPC:
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
