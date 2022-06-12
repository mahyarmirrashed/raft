"""Defines the server handling different operations."""

from random import uniform
from socket import SOL_SOCKET, socket, AF_INET, SOCK_DGRAM, SO_REUSEADDR
from time import time
from typing import List, Set, Union

from pydantic import BaseModel, Extra, NonNegativeInt, StrictBool, ValidationError
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

TIMEOUT_LOWER_BOUND: float = 10  # seconds
TIMEOUT_UPPER_BOUND: float = 20  # seconds


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
    extra = Extra.allow

  def _id(self) -> Address:
    """Return server identification."""
    if self.sock is not None:
      host, port = self.sock.getsockname()
      return Address(host=host, port=port)
    else:
      raise RuntimeError("Ensure that socket is set.")

  def _role_demote_if_necessary(self, capture: _CaptureTerm) -> None:
    """Convert to follower role if term is defined and larger."""
    if capture.term is not None and capture.term > self._role.current_term:
      self._role.update_current_term(NonNegativeInt(capture.term))
      self._role.update_voted_for(None)

      if not isinstance(self._role, FollowerRole):
        self._role_demote_to_follower()

  def _role_demote_to_follower(self) -> None:
    """Demote current candidate/leader role to follower role."""
    print(f"INFO: Demoted to term {self._role.current_term} follower.")
    self._role = FollowerRole(**self._role.dict())

  def _role_promote_to_candidate(self) -> None:
    """Promote current follower role to candidate role."""
    print(f"INFO: Promoted to term {self._role.current_term} candidate.")
    self._role = CandidateRole(**self._role.dict())

  def _role_promote_to_leader(self) -> None:
    """Promote current candidate role to leader role."""
    print(f"INFO: Promoted to term {self._role.current_term} leader.")
    self._role = LeaderRole(
      **self._role.dict(),
      next_index={address: len(self._role.log) - 1 for address in self.addresses},
      match_index={address: 0 for address in self.addresses},
    )

  def _rpc_handle_append_entries_request(self, req: AppendEntriesRPCRequest) -> RPC:
    """Implement the AppendEntries RPC request according to Figure 3.1."""
    res: AppendEntriesRPCResponse
    previous_entry: Union[Entry, None] = self._role.log[req.previous_log_index]

    print("INFO: Handling AppendEntries RPC request.")

    self._timeout_reset()

    if req.term < self._role.current_term:
      res = AppendEntriesRPCResponse(term=self._role.current_term, success=False)
    elif previous_entry is None or req.previous_log_term != previous_entry.term:
      res = AppendEntriesRPCResponse(term=self._role.current_term, success=False)
    else:
      # raft is not byzantine, receiving an append entries means to demote to follower
      if not isinstance(self._role, FollowerRole):
        self._role_demote_to_follower()
      # ensure entry monoticity
      assert all(x.index + 1 == y.index for x, y in zip(req.entries, req.entries[1:]))
      # update log with monotonic entries
      for entry in req.entries:
        self._role.update_log(entry)
      # update commit index if necessary
      if req.leader_commit_index > self._role.commit_index:
        self._role.commit_index = min(req.leader_commit_index, len(self._role.log) - 1)
      # successfully appended entries
      res = AppendEntriesRPCResponse(term=self._role.current_term, success=True)

    return RPC(
      direction=RPCDirection.RESPONSE,
      type=RPCType.APPEND_ENTRIES,
      content=res.json(),
    )

  def _rpc_handle_append_entries_response(
    self, res: AppendEntriesRPCResponse, sender: Address
  ) -> None:
    """Implement the AppendEntries RPC response according to Figure 3.1."""
    print(f"INFO: Handling AppendEntries RPC response: {res}.")

    if isinstance(self._role, LeaderRole):
      if res.success:
        self._role.next_index[sender] += 1
        self._role.match_index[sender] += 1
      else:
        self._role.next_index[sender] -= 1

  def _rpc_handle_request_vote_request(self, req: RequestVoteRPCRequest) -> RPC:
    """Implement the RequestVote RPC request according to Figure 3.1."""
    res: RequestVoteRPCResponse
    last_entry: Union[Entry, None] = self._role.log[-1]
    assert last_entry is not None

    print("INFO: Handling RequestVote RPC request.")

    self._timeout_reset()

    at_least_as_up_to_date = req.last_log_term > last_entry.term or (
      req.last_log_term == last_entry.term and req.last_log_index >= last_entry.index
    )

    if req.term < self._role.current_term:
      res = RequestVoteRPCResponse(term=self._role.current_term, vote_granted=False)
    elif (
      self._role.voted_for is None or self._role.voted_for == req.candidate_identity
    ) and at_least_as_up_to_date:
      self._role.update_voted_for(req.candidate_identity)
      res = RequestVoteRPCResponse(term=self._role.current_term, vote_granted=True)
    else:
      res = RequestVoteRPCResponse(term=self._role.current_term, vote_granted=False)

    return RPC(
      direction=RPCDirection.RESPONSE,
      type=RPCType.REQUEST_VOTE,
      content=res.json(),
    )

  def _rpc_handle_request_vote_response(
    self, res: RequestVoteRPCResponse, sender: Address
  ) -> None:
    """Implement the RequestVote RPC response according to Figure 3.1."""

    print(f"INFO: Handling RequestVote RPC response: {res}.")

    if isinstance(self._role, CandidateRole) and res.vote_granted:
      self._votes.add(sender)

      # if majority attained (syntax is from Raft's TLA+ specification)
      if len(self._votes) * 2 > len(self.addresses):
        self._role_promote_to_leader()
        self._rpc_send_append_entries()
        self._timeout_reset(leader=True)

  def _rpc_send(self, rpc: RPC, addr: Address) -> None:
    """Send an RPC to another server."""
    if self.sock is not None:
      try:
        self.sock.sendto(f"{rpc.json()}\n".encode(), (addr.host, addr.port))
      except:
        print("ERROR: Failed to send RPC.")
    else:
      print("ERROR: Socket is not initialized.")

  def _rpc_send_append_entries(self) -> None:
    """Send an AppendEntry RPC to everyone but us."""
    if isinstance(self._role, LeaderRole):
      leader: LeaderRole = self._role

      for address in self.addresses:
        if address != self._id():
          previous_entry = self._role.log[leader.next_index[address] - 1]

          self._rpc_send(
            RPC(
              direction=RPCDirection.REQUEST,
              type=RPCType.APPEND_ENTRIES,
              content=AppendEntriesRPCRequest(
                term=self._role.current_term,
                leader_identity=self._id(),
                previous_log_index=previous_entry.index,
                previous_log_term=previous_entry.term,
                entries=self._role.log[leader.next_index[address] :],
                leader_commit_index=self._role.commit_index,
              ).json(),
            ),
            address,
          )

  def _timeout_reset(self, leader: StrictBool = False) -> None:
    """Create new timeout value."""
    print("INFO: Resetting timeout value.")

    self.timeout = uniform(TIMEOUT_LOWER_BOUND, TIMEOUT_UPPER_BOUND)
    # shorter timeout for leader
    if leader:
      self.timeout /= 3
    # offset to current time
    self.timeout += time()

  def apply_commits(self) -> None:
    """Instruct role to handle applying commits to the database."""
    self._role.apply_commits()

  def init_sock(self, port: NonNegativeInt) -> None:
    """Initialize the socket."""
    try:
      self.sock = socket(AF_INET, SOCK_DGRAM)
      self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
      self.sock.bind(("127.0.0.1", port))
    except:
      print("ERROR: Failed to set up socket.")
      exit(1)

  def is_leader(self) -> StrictBool:
    """Indicate if the server is currently term leader."""
    return isinstance(self._role, LeaderRole)

  def is_timed_out(self) -> StrictBool:
    """Indicate if the server has timed out."""
    return time() > self.timeout

  def start_election(self) -> None:
    """Start election process."""
    if self.sock is not None:
      self._role.update_current_term(NonNegativeInt(self._role.current_term + 1))
      self._role_promote_to_candidate()
      self._role.update_voted_for(self._id())
      self._votes = {self._id()}
      self._timeout_reset()

      rpc = RPC(
        direction=RPCDirection.REQUEST,
        type=RPCType.REQUEST_VOTE,
        content=RequestVoteRPCRequest(
          term=self._role.current_term,
          candidate_identity=self._id(),
          last_log_index=self._role.log[-1].index,
          last_log_term=self._role.log[-1].term,
        ).json(),
      )

      for address in self.addresses:
        if address != self._id():
          self._rpc_send(rpc, address)

  def start_heartbeat(self) -> None:
    """Start leader heartbeat."""
    if isinstance(self._role, LeaderRole):
      match_indices = self._role.match_index.values()
      N = min(match_indices)

      while (
        N < len(self._role.log)
        and N > self._role.commit_index
        and sum(idx >= N for idx in match_indices) * 2 > len(self.addresses)
        and self._role.log[N].term == self._role.current_term
      ):
        self._role.commit_index = N
        N += 1

      self._rpc_send_append_entries()
      self._timeout_reset(leader=True)

  def rpc_handle(self, rpc: RPC, sender: Address) -> None:
    """Handle an incoming RPC request."""
    try:
      self._role_demote_if_necessary(_CaptureTerm.parse_raw(rpc.content))

      if rpc.direction == RPCDirection.REQUEST:
        res: Union[RPC, None] = None

        if rpc.type == RPCType.APPEND_ENTRIES:
          res = self._rpc_handle_append_entries_request(
            AppendEntriesRPCRequest.parse_raw(rpc.content)
          )
        elif rpc.type == RPCType.REQUEST_VOTE:
          res = self._rpc_handle_request_vote_request(
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
          self._rpc_send(res, sender)
      elif rpc.direction == RPCDirection.RESPONSE:
        if rpc.type == RPCType.APPEND_ENTRIES:
          self._rpc_handle_append_entries_response(
            AppendEntriesRPCResponse.parse_raw(rpc.content),
            sender,
          )
        elif rpc.type == RPCType.REQUEST_VOTE:
          self._rpc_handle_request_vote_response(
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
