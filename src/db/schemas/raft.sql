CREATE TABLE IF NOT EXISTS Entries (
  id INTEGER PRIMARY KEY NOT NULL CHECK(id >= 0),
  term INTEGER NOT NULL CHECK(id >= 0),
  username TEXT NOT NULL CHECK (
    LENGTH(username) <= 64
    AND username NOT LIKE '%[^a-zA-Z0-9]%'
  ),
  balance INTEGER NOT NULL DEFAULT 0
);