CREATE TABLE IF NOT EXISTS Bank (
  username TEXT PRIMARY KEY NOT NULL CHECK (
    LENGTH(username) <= 64
    AND username NOT LIKE '%[^a-zA-Z0-9]%'
  ),
  balance INTEGER NOT NULL DEFAULT 0
);