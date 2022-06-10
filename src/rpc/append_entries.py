"""Defines the AppendEntries RPC (Remote Procedure Call) as per Figure 3.1."""

from _base import BaseRPCRequest, BaseRPCResponse


class AppendEntriesRPCRequest(BaseRPCRequest):
  """Implements AppendEntries RPC request arguments."""

  @property
  def entries(self):
    pass

  @property
  def leader_commit_index(self):
    pass

  @property
  def leader_identity(self):
    pass

  @property
  def previous_log_index(self):
    pass

  @property
  def previous_log_term(self):
    pass

  @property
  def term(self):
    pass


class AppendEntriesRPCResponse(BaseRPCResponse):
  """Implements AppendEntries RPC response results."""

  @property
  def success(self):
    pass

  @property
  def term(self):
    pass
