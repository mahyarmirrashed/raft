"""Defines the RemoveServer RPC (Remote Procedure Call) as per Figure 4.1."""

from . import BaseRPCRequest, BaseRPCResponse


class RemoveServerRPCRequest(BaseRPCRequest):
  """Implements RemoveServer RPC request arguments."""

  @property
  def old_server(self):
    pass


class RemoveServerRPCResponse(BaseRPCResponse):
  """Implements RemoveServer RPC response results."""

  @property
  def status(self):
    pass

  @property
  def leader_hint(self):
    pass
