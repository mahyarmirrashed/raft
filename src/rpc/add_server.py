"""Defines the AddServer RPC (Remote Procedure Call) as per Figure 4.1."""

from typing import Union

from pydantic import StrictBool
from utils import Address

from . import BaseRPCRequest, BaseRPCResponse


class AddServerRPCRequest(BaseRPCRequest):
  """Implements AddServer RPC request arguments."""

  new_server: Address


class AddServerRPCResponse(BaseRPCResponse):
  """Implements AddServer RPC response results."""

  status: StrictBool
  leader_hint: Union[Address, None]
