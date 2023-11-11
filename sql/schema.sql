PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR(20) PRIMARY KEY NOT NULL,
  fullname VARCHAR(40) NOT NULL,
  email VARCHAR(40) NOT NULL,
  password VARCHAR(256) NOT NULL,
  created DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME'))
);

CREATE TABLE utility_data(
  username VARCHAR(20) PRIMARY KEY NOT NULL,
  electricity_rates VARCHAR(40) NOT NULL,
  water_rates VARCHAR(40) NOT NULL,
  gas_rates VARCHAR(40) NOT NULL,
  garbage_rates VARCHAR(40) NOT NULL
);