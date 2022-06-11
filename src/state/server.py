"""Defines the server handling different operations."""

from random import uniform

from db import DatabaseDriver
from pydantic import BaseModel, ValidationError
from roles import BaseRole, CandidateRole, FollowerRole, LeaderRole
from rpc import (
  AddServerRPCRequest,
  AddServerRPCResponse,
  AppendEntriesRPCRequest,
  AppendEntriesRPCResponse,
  RemoveServerRPCRequest,
  RemoveServerRPCResponse,
  RequestVoteRPCRequest,
  RequestVoteRPCResponse,
)
from utils.rpc import RPC, RPCDirection, RPCType

TIMEOUT_LOWER_BOUND: float = 0.150  # seconds
TIMEOUT_UPPER_BOUND: float = 0.300  # seconds


class Server(BaseModel):
  """Define server model."""

  _driver: DatabaseDriver = DatabaseDriver()
  role: BaseRole = FollowerRole(
    current_term=0,
    voted_for=None,
    log=[],
    commit_index=0,
    last_applied_index=0,
  )
  timeout: float = uniform(TIMEOUT_LOWER_BOUND, TIMEOUT_UPPER_BOUND)

  @classmethod
  def _role_demote_to_follower(cls) -> None:
    """Demote current candidate/leader role to follower role."""
    Server.role = FollowerRole(**cls.role.dict())

  @classmethod
  def _role_promote_to_candidate(cls) -> None:
    """Promote current follower role to candidate role."""
    Server.role = CandidateRole(**cls.role.dict())

  @classmethod
  def _role_promote_to_leader(cls) -> None:
    """Promote current candidate role to leader role."""
    Server.role = LeaderRole(**cls.role.dict(), next_index=[], match_index=[])

  @classmethod
  def _rpc_handle_append_entries_request(cls, req: AppendEntriesRPCRequest) -> None:
    pass

  @classmethod
  def _rpc_handle_append_entries_response(cls, res: AppendEntriesRPCResponse) -> None:
    pass

  @classmethod
  def _rpc_handle_request_vote_request(cls, req: RequestVoteRPCRequest) -> None:
    pass

  @classmethod
  def _rpc_handle_request_vote_response(cls, res: RequestVoteRPCResponse) -> None:
    pass

  @classmethod
  def rpc_handle(cls, rpc: RPC) -> None:
    """Handle an incoming RPC request."""

    try:
      if rpc.type == RPCType.APPEND_ENTRY:
        if rpc.direction == RPCDirection.REQUEST:
          cls._rpc_handle_append_entries_request(
            AppendEntriesRPCRequest.parse_raw(rpc.content)
          )
        elif rpc.direction == RPCDirection.RESPONSE:
          cls._rpc_handle_append_entries_response(
            AppendEntriesRPCResponse.parse_raw(rpc.content)
          )
      elif rpc.type == RPCType.REQUEST_VOTE:
        if rpc.direction == RPCDirection.REQUEST:
          cls._rpc_handle_request_vote_request(
            RequestVoteRPCRequest.parse_raw(rpc.content)
          )
        elif rpc.direction == RPCDirection.RESPONSE:
          cls._rpc_handle_request_vote_response(
            RequestVoteRPCResponse.parse_raw(rpc.content)
          )
      elif rpc.type == RPCType.ADD_SERVER:
        raise NotImplementedError("AddServer RPC is not implemented yet.")
      elif rpc.type == RPCType.REMOVE_SERVER:
        raise NotImplementedError("RemoveServer RPC is not implemented yet.")
      elif rpc.type == RPCType.INSTALL_SNAPSHOT:
        raise NotImplementedError("InstallSnapshot RPC is not implemented yet.")
      elif rpc.type == RPCType.REGISTER_CLIENT:
        raise NotImplementedError("RegisterClient RPC is not implemented yet.")
      elif rpc.type == RPCType.CLIENT_REQUEST:
        raise NotImplementedError("ClientRequest RPC is not implemented yet.")
      elif rpc.type == RPCType.CLIENT_QUERY:
        raise NotImplementedError("ClientQuery RPC is not implemented yet.")
    except ValidationError:
      print("ERROR: Invalid RPC request/response received.")
    except:
      print("CRITICAL: Deadly unknown exception occurred.")
