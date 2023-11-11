"""Insta485 development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = b'\xf9MR\x92\xf3\x13\xfb\xc3\xd3<\xe5\xc5\x15a_\xa6H\xb0\x16\x17'
's\x1b\x0b\n'
SESSION_COOKIE_NAME = 'login'

# File Upload to var/uploads/
BILL_BUDDIES_ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024


DATABASE_FILENAME = BILL_BUDDIES_ROOT/'var'/'bill_buddies.sqlite3'
