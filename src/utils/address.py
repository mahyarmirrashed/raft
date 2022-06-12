"""Defines an address."""

import re

from pydantic import ConstrainedInt, ConstrainedStr

from utils.models import FrozenModel

# https://stackoverflow.com/questions/106179/regular-expression-to-match-dns-hostname-or-ip-address
REGEX_HOSTNAME = r"(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])"
REGEX_IP_ADDRESS = r"(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
# compile into final regular expression
REGEX_SOCKET_ADDRESS = f"^({REGEX_HOSTNAME}|{REGEX_IP_ADDRESS})$"


class _Host(ConstrainedStr):
  regex = re.compile(REGEX_SOCKET_ADDRESS)


class _Port(ConstrainedInt):
  ge = 0
  lt = 65536


class Address(FrozenModel):
  host: _Host = _Host("0.0.0.0")
  port: _Port
