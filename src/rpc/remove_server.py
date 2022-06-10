"""Defines the RemoveServer RPC (Remote Procedure Call) as per Figure 4.1."""

from typing import Union

from pydantic import StrictBool

from . import Address, BaseRPCRequest, BaseRPCResponse


class RemoveServerRPCRequest(BaseRPCRequest):
  """Implements RemoveServer RPC request arguments."""

  old_server: Address


class RemoveServerRPCResponse(BaseRPCResponse):
  """Implements RemoveServer RPC response results."""

  status: StrictBool
  leader_hint: Union[Address, None]
