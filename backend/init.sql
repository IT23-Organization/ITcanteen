CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  user_id     INTEGER NOT NULL,
  product_ids TEXT    NOT NULL, -- JSON array of integers
  total       REAL    NOT NULL,
  paid        BOOLEAN NOT NULL
);

CREATE TABLE users (
  user_id   INTEGER PRIMARY KEY,
  username  TEXT    NOT NULL UNIQUE,
  password  TEXT    NOT NULL, -- hashed password
  user_type TEXT    NOT NULL  -- "USER" | "STORE" | "ADMIN"
);

CREATE TABLE dream_session (
  id         TEXT PRIMARY KEY,
  label      TEXT NOT NULL,
  expires_at REAL NOT NULL,
  payload    TEXT NOT NULL
);