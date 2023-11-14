PRAGMA foreign_keys = ON;

INSERT INTO users(username, fullname, password)
VALUES ('awdeorio', 'Andrew DeOrio', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8'),
('jflinn', 'Jason Flinn', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8'),
('michjc', 'Michael Cafarella', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8'),
('jag', 'H.V. Jagadish', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO usage (username, month, electricity_bill, water_bill, gas_bill, garbage_bill)
VALUES 
    ('awdeorio', '2023-01-01', 100, 50, 30, 20),
    ('awdeorio', '2023-02-01', 110, 55, 33, 22),
    ('jflinn', '2023-01-01', 90, 45, 27, 18),
    ('jflinn', '2023-02-01', 95, 48, 29, 19),
    ('michjc', '2023-01-01', 120, 60, 36, 24),
    ('michjc', '2023-02-01', 130, 65, 39, 26),
    ('jag', '2023-01-01', 80, 40, 24, 16),
    ('jag', '2023-02-01', 85, 42, 25, 17);