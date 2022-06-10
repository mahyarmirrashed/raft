"""Defines the RequestVote RPC (Remote Procedure Call) as per Figure 3.1."""

from db.objects import Identity
from pydantic import NonNegativeInt, StrictBool
from pydantic.dataclasses import dataclass

from . import BaseRPCRequest, BaseRPCResponse


@dataclass(frozen=True)
class RequestVoteRPCRequest(BaseRPCRequest):
  """Implements RequestVote RPC request arguments."""

  term: NonNegativeInt
  candidate_identity: Identity
  last_log_index: NonNegativeInt
  last_log_term: NonNegativeInt


@dataclass(frozen=True)
class RequestVoteRPCResponse(BaseRPCResponse):
  """Implements RequestVote RPC response results."""

  term: NonNegativeInt
  vote_granted: StrictBool
