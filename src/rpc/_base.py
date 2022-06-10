"""Defines the base RPC (Remote Procedure Call)."""

from orjson import loads, dumps
from pydantic import BaseModel


class BaseRPC(BaseModel):
  """Base RPC message."""

  class Config:
    json_loads = loads
    json_dumps = lambda v, *, default: dumps(v, default=default).decode()


class BaseRPCRequest(BaseRPC):
  """Base RPC Request type."""

  pass


class BaseRPCResponse(BaseRPC):
  """Base RPC Response type."""

  pass
