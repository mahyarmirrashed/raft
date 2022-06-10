"""Defines the RequestVote RPC (Remote Procedure Call) as per Figure 3.1."""

from _base import BaseRPCRequest, BaseRPCResponse


class RequestVoteRPCRequest(BaseRPCRequest):
  """Implements RequestVote RPC request arguments."""

  @property
  def candidate_identity(self):
    pass

  @property
  def last_log_index(self):
    pass

  @property
  def last_log_term(self):
    pass

  @property
  def term(self):
    pass


class RequestVoteRPCResponse(BaseRPCResponse):
  """Implements RequestVote RPC response results."""

  @property
  def vote_granted(self):
    pass

  @property
  def term(self):
    pass
