"""Defines the AppendEntries RPC (Remote Procedure Call) as per Figure 3.1."""

from typing import List

from db.objects import Entry, Identity
from pydantic import NonNegativeInt, StrictBool

from . import BaseRPCRequest, BaseRPCResponse


class AppendEntriesRPCRequest(BaseRPCRequest):
  """Implements AppendEntries RPC request arguments."""

  term: NonNegativeInt
  leader_identity: Identity
  previous_log_index: NonNegativeInt
  previous_log_term: NonNegativeInt
  entries: List[Entry]
  leader_commit_index: NonNegativeInt


class AppendEntriesRPCResponse(BaseRPCResponse):
  """Implements AppendEntries RPC response results."""

  term: NonNegativeInt
  success: StrictBool
