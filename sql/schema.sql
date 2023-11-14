PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR(20) PRIMARY KEY NOT NULL,
  password VARCHAR(256) NOT NULL,
  fullname VARCHAR(60) NOT NULL,
  created DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME'))
);

CREATE TABLE usage(
  id SERIAL PRIMARY KEY,
  username VARCHAR(20) NOT NULL,
  month DATE NOT NULL,
  electricity_bill DECIMAL(10, 2) NOT NULL,
  water_bill DECIMAL(10, 2) NOT NULL,
  gas_bill DECIMAL(10, 2) NOT NULL,
  garbage_bill DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY (username) REFERENCES users(username)
);