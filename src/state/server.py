"""Defines the server handling different operations."""

from random import uniform
from socket import SOL_SOCKET, socket, AF_INET, SOCK_DGRAM, SO_REUSEADDR
from time import time
from typing import List, Set, Union

from pydantic import BaseModel, NonNegativeInt, StrictBool, ValidationError
from db import Entry
from roles import BaseRole, CandidateRole, FollowerRole, LeaderRole
from rpc import (
  AppendEntriesRPCRequest,
  AppendEntriesRPCResponse,
  RequestVoteRPCRequest,
  RequestVoteRPCResponse,
)
from utils.address import Address
from utils.models import FrozenModel
from utils.rpc import RPC, RPCDirection, RPCType

# XXX
TIMEOUT_LOWER_BOUND: float = 10  # seconds
TIMEOUT_UPPER_BOUND: float = 11  # seconds


class _CaptureTerm(FrozenModel):
  term: Union[NonNegativeInt, None] = None


class Server(BaseModel):
  """Define server model."""

  _role: BaseRole = FollowerRole(commit_index=0, last_applied_index=0)
  _votes: Set[Address] = set()
  sock: Union[socket, None] = None
  addresses: List[Address]
  timeout: float = time() + uniform(TIMEOUT_LOWER_BOUND, TIMEOUT_UPPER_BOUND)

  class Config:
    arbitrary_types_allowed = True

  @classmethod
  def _id(cls) -> Address:
    """Return server identification."""
    if cls.sock is not None:
      host, port = cls.sock.getsockname()
      return Address(host=host, port=port)
    else:
      raise RuntimeError("Ensure that socket is set.")

  @classmethod
  def _role_demote_if_necessary(cls, capture: _CaptureTerm) -> None:
    """Convert to follower role if term is defined and larger."""
    if capture.term is not None and capture.term > cls._role.current_term:
      cls._role.update_current_term(capture.term)
      cls._role.update_voted_for(None)
      cls._role_demote_to_follower()

  @classmethod
  def _role_demote_to_follower(cls) -> None:
    """Demote current candidate/leader role to follower role."""
    cls._role = FollowerRole(**cls._role.dict())

  @classmethod
  def _role_promote_to_candidate(cls) -> None:
    """Promote current follower role to candidate role."""
    cls._role = CandidateRole(**cls._role.dict())

  @classmethod
  def _role_promote_to_leader(cls) -> None:
    """Promote current candidate role to leader role."""
    cls._role = LeaderRole(
      **cls._role.dict(),
      next_index={address: len(cls._role.log) - 1 for address in cls.addresses},
      match_index={address: 0 for address in cls.addresses},
    )

  @classmethod
  def _rpc_handle_append_entries_request(cls, req: AppendEntriesRPCRequest) -> RPC:
    """Implement the AppendEntries RPC request according to Figure 3.1."""
    res: AppendEntriesRPCResponse
    previous_entry: Union[Entry, None] = cls._role.log[req.previous_log_index]

    cls._timeout_reset()

    if req.term < cls._role.current_term:
      res = AppendEntriesRPCResponse(term=cls._role.current_term, success=False)
    elif previous_entry is None or req.previous_log_term != previous_entry.term:
      res = AppendEntriesRPCResponse(term=cls._role.current_term, success=False)
    else:
      # raft is not byzantine, receiving an append entries means to demote to follower
      if not isinstance(cls._role, FollowerRole):
        cls._role_demote_to_follower()
      # ensure entry monoticity
      assert all(x.index + 1 == y.index for x, y in zip(req.entries, req.entries[1:]))
      # update log with monotonic entries
      for entry in req.entries:
        cls._role.update_log(entry)
      # update commit index if necessary
      if req.leader_commit_index > cls._role.commit_index:
        cls._role.commit_index = min(req.leader_commit_index, len(cls._role.log) - 1)
      # successfully appended entries
      res = AppendEntriesRPCResponse(term=cls._role.current_term, success=True)

    return RPC(
      direction=RPCDirection.RESPONSE,
      type=RPCType.APPEND_ENTRIES,
      content=res.json(),
    )

  @classmethod
  def _rpc_handle_append_entries_response(
    cls, res: AppendEntriesRPCResponse, sender: Address
  ) -> None:
    """Implement the AppendEntries RPC response according to Figure 3.1."""
    if isinstance(cls._role, LeaderRole):
      if res.success:
        cls._role.next_index[sender] += 1
        cls._role.match_index[sender] += 1
      else:
        cls._role.next_index[sender] -= 1

  @classmethod
  def _rpc_handle_request_vote_request(cls, req: RequestVoteRPCRequest) -> RPC:
    """Implement the RequestVote RPC request according to Figure 3.1."""
    res: RequestVoteRPCResponse
    last_entry: Union[Entry, None] = cls._role.log[-1]
    assert last_entry is not None

    cls._timeout_reset()

    if req.term < cls._role.current_term:
      res = RequestVoteRPCResponse(term=cls._role.current_term, vote_granted=False)
    elif (
      cls._role.voted_for is None or cls._role.voted_for == req.candidate_identity
    ) and (
      req.last_log_term > last_entry.term or req.last_log_index > last_entry.index
    ):
      cls._role.update_voted_for(req.candidate_identity)
      res = RequestVoteRPCResponse(term=cls._role.current_term, vote_granted=True)
    else:
      res = RequestVoteRPCResponse(term=cls._role.current_term, vote_granted=False)

    return RPC(
      direction=RPCDirection.RESPONSE,
      type=RPCType.REQUEST_VOTE,
      content=res.json(),
    )

  @classmethod
  def _rpc_handle_request_vote_response(
    cls, res: RequestVoteRPCResponse, sender: Address
  ) -> None:
    """Implement the RequestVote RPC response according to Figure 3.1."""
    if isinstance(cls._role, CandidateRole) and res.vote_granted:
      cls._votes.add(sender)

      # if majority attained (syntax is from Raft's TLA+ specification)
      if len(cls._votes) * 2 > len(cls.addresses):
        cls._role_promote_to_leader()
        cls._rpc_send_append_entries()

  @classmethod
  def _rpc_send(cls, rpc: RPC, addr: Address) -> None:
    """Send an RPC to another server."""
    if cls.sock is not None:
      try:
        cls.sock.sendto(f"{rpc.json()}\n".encode(), (addr.host, addr.port))
      except:
        print("ERROR: Failed to send RPC.")
    else:
      print("ERROR: Socket is not initialized.")

  @classmethod
  def _rpc_send_append_entries(cls) -> None:
    """Send an AppendEntry RPC to everyone but us."""
    if isinstance(cls._role, LeaderRole):
      leader: LeaderRole = cls._role

      for address in cls.addresses:
        if address != cls._id():
          previous_entry = cls._role.log[leader.next_index[address] - 1]

          cls._rpc_send(
            RPC(
              direction=RPCDirection.REQUEST,
              type=RPCType.APPEND_ENTRIES,
              content=AppendEntriesRPCRequest(
                term=cls._role.current_term,
                leader_identity=cls._id(),
                previous_log_index=previous_entry.index,
                previous_log_term=previous_entry.term,
                entries=cls._role.log[leader.next_index[address] :],
                leader_commit_index=cls._role.commit_index,
              ).json(),
            ),
            address,
          )

  @classmethod
  def _timeout_reset(cls, leader: StrictBool = False) -> None:
    """Create new timeout value."""
    cls.timeout = time() + uniform(TIMEOUT_LOWER_BOUND, TIMEOUT_UPPER_BOUND)
    # shorter timeout for
    if leader:
      cls.timeout -= TIMEOUT_LOWER_BOUND / 3

  @classmethod
  def apply_commits(cls) -> None:
    """Instruct role to handle applying commits to the database."""
    cls._role.apply_commits()

  @classmethod
  def init_sock(cls, port: NonNegativeInt) -> None:
    """Initialize the socket."""
    try:
      cls.sock = socket(AF_INET, SOCK_DGRAM)
      cls.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
      cls.sock.bind(("", port))
    except:
      print("ERROR: Failed to set up socket.")
      exit(1)

  @classmethod
  def is_leader(cls) -> StrictBool:
    """Indicate if the server is currently term leader."""
    return isinstance(cls._role, LeaderRole)

  @classmethod
  def is_timed_out(cls) -> StrictBool:
    """Indicate if the server has timed out. Leaders cannot time out."""
    return not isinstance(cls._role, LeaderRole) and time() > cls.timeout

  @classmethod
  def start_election(cls) -> None:
    """Start election process."""
    if cls.sock is not None:
      cls._role_promote_to_candidate()
      cls._role.update_current_term(cls._role.current_term + 1)
      cls._role.update_voted_for(cls._id())
      cls._votes = {cls._id()}
      cls._timeout_reset()

      rpc = RPC(
        direction=RPCDirection.REQUEST,
        type=RPCType.REQUEST_VOTE,
        content=RequestVoteRPCRequest(
          term=cls._role.current_term,
          candidate_identity=cls._id(),
          last_log_index=cls._role.log[-1].index,
          last_log_term=cls._role.log[-1].term,
        ).json(),
      )

      for address in cls.addresses:
        if address != cls._id():
          cls._rpc_send(rpc, address)

  @classmethod
  def start_heartbeat(cls) -> None:
    """Start leader heartbeat."""
    if isinstance(cls._role, LeaderRole):
      match_indices = cls._role.match_index.values()
      N = min(match_indices)

      while (
        N > cls._role.commit_index
        and sum(idx >= N for idx in match_indices) * 2 > len(cls.addresses)
        and cls._role.log[N].term == cls._role.current_term
      ):
        cls._role.commit_index = N
        N += 1

      cls._rpc_send_append_entries()

  @classmethod
  def rpc_handle(cls, rpc: RPC, sender: Address) -> None:
    """Handle an incoming RPC request."""
    try:
      cls._role_demote_if_necessary(_CaptureTerm.parse_raw(rpc.content))

      if rpc.direction == RPCDirection.REQUEST:
        res: Union[RPC, None] = None

        if rpc.type == RPCType.APPEND_ENTRIES:
          print("INFO: Handling AppendEntries RPC request.")
          res = cls._rpc_handle_append_entries_request(
            AppendEntriesRPCRequest.parse_raw(rpc.content)
          )
        elif rpc.type == RPCType.REQUEST_VOTE:
          print("INFO: Handling RequestVote RPC request.")
          res = cls._rpc_handle_request_vote_request(
            RequestVoteRPCRequest.parse_raw(rpc.content)
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

        if isinstance(res, RPC):
          cls._rpc_send(res, sender)
      elif rpc.direction == RPCDirection.RESPONSE:
        if rpc.type == RPCType.APPEND_ENTRIES:
          print("INFO: Handling AppendEntries RPC response.")
          cls._rpc_handle_append_entries_response(
            AppendEntriesRPCResponse.parse_raw(rpc.content),
            sender,
          )
        elif rpc.type == RPCType.REQUEST_VOTE:
          print("INFO: Handling RequestVote RPC response.")
          cls._rpc_handle_request_vote_response(
            RequestVoteRPCResponse.parse_raw(rpc.content),
            sender,
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
    except NotImplementedError as e:
      print(f"ERROR: {e}")
    except:
      print("CRITICAL: Deadly unknown exception occurred.")
