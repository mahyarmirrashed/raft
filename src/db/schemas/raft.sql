CREATE TABLE IF NOT EXISTS Entries (
  id INTEGER PRIMARY KEY NOT NULL CHECK(id >= 0),
  term INTEGER NOT NULL CHECK(id >= 0),
  username TEXT NOT NULL CHECK(
    LENGTH(username) <= 64
    AND username NOT LIKE '%[^a-zA-Z0-9]%'
  ),
  balance INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Identities (
  socket_address_hash TEXT PRIMARY KEY NOT NULL CHECK(
    LENGTH(socket_address_hash) = 64,
    AND socket_address_hash NOT LIKE '%[^a-zA-Z0-9]%'
  ),
  socket_address TEXT NOT NULL
);