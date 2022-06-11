"""Defines the RemoveServer RPC (Remote Procedure Call) as per Figure 4.1."""

from typing import Union

from pydantic import StrictBool
from utils import Address

from . import BaseRPC


class RemoveServerRPCRequest(BaseRPC):
  """Implements RemoveServer RPC request arguments."""

  old_server: Address


class RemoveServerRPCResponse(BaseRPC):
  """Implements RemoveServer RPC response results."""

  status: StrictBool
  leader_hint: Union[Address, None] = None
