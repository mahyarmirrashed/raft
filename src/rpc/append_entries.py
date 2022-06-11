"""Defines the AppendEntries RPC (Remote Procedure Call) as per Figure 3.1."""

from typing import List

from db import Entry
from pydantic import NonNegativeInt, StrictBool
from utils import Address

from . import BaseRPC


class AppendEntriesRPCRequest(BaseRPC):
  """Implements AppendEntries RPC request arguments."""

  term: NonNegativeInt
  leader_identity: Address
  previous_log_index: NonNegativeInt
  previous_log_term: NonNegativeInt
  entries: List[Entry]
  leader_commit_index: NonNegativeInt


class AppendEntriesRPCResponse(BaseRPC):
  """Implements AppendEntries RPC response results."""

  term: NonNegativeInt
  success: StrictBool
