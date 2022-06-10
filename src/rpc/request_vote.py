"""Defines the RequestVote RPC (Remote Procedure Call) as per Figure 3.1."""

from pydantic import NonNegativeInt, StrictBool
from utils import Address

from . import BaseRPCRequest, BaseRPCResponse


class RequestVoteRPCRequest(BaseRPCRequest):
  """Implements RequestVote RPC request arguments."""

  term: NonNegativeInt
  candidate_identity: Address
  last_log_index: NonNegativeInt
  last_log_term: NonNegativeInt


class RequestVoteRPCResponse(BaseRPCResponse):
  """Implements RequestVote RPC response results."""

  term: NonNegativeInt
  vote_granted: StrictBool
