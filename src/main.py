"""Define server main loop here."""

from argparse import ArgumentParser
from pathlib import Path
from select import select
from time import time

from orjson import loads

from state import Server
from utils import RPC, Address

###############################################################################
# SET UP ARGUMENT PARSER
###############################################################################

# ./main.py PORT
parser = ArgumentParser(description="Raft server.")

parser.add_argument(
  "--port",
  type=int,
  required=True,
  help="server port number",
)

args = parser.parse_args()

###############################################################################
# SET UP SERVER
###############################################################################


def main() -> None:
  """Program enters here."""

  with open(Path(__file__).parent / "config.json", mode="r") as fp:
    config = loads(fp.read())

  ports = map(int, config["ports"])
  # ensure other servers are aware of us
  assert args.port in ports

  # inialize server
  server = Server(addresses=[Address(port=port) for port in ports])
  server.init_sock(args.port)

  print(f"INFO: Server is starting on 127.0.0.1:{args.port}...")

  try:
    while True:
      readable, _, exceptional = select(
        [server.sock], [], [], max(0, server.timeout - time())
      )

      if server.is_timed_out():
        if server.is_leader():
          server.start_heartbeat()
        else:
          server.start_election()

      for sock in readable:
        data, addr = sock.recvfrom(1024)
        for payload in data.decode().splitlines(keepends=True):
          server.rpc_handle(RPC.parse_raw(payload), Address(host=addr[0], port=addr[1]))

      for sock in exceptional:
        if sock is server.sock:
          server.init_sock(args.port)

      # apply commits when commit index is incremented
      server.apply_commits()

  except KeyboardInterrupt:
    print("INFO: Server ending normally...")
  except Exception as e:
    print(f"CRITICAL: {e}")

  print("End of processing.")


if __name__ == "__main__":
  main()
