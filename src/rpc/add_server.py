"""Defines the AddServer RPC (Remote Procedure Call) as per Figure 4.1."""

from _base import BaseRPCRequest, BaseRPCResponse


class AddServerRPCRequest(BaseRPCRequest):
  """Implements AddServer RPC request arguments."""

  @property
  def new_server(self):
    pass


class AddServerRPCResponse(BaseRPCResponse):
  """Implements AddServer RPC response results."""

  @property
  def status(self):
    pass

  @property
  def leader_hint(self):
    pass
