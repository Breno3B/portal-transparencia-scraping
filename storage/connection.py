"""MySQL connection and strict identifier validation."""
import os
import re
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def identifier(value):
    if not value or re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", value) is None:
        raise ValueError(f"Invalid SQL identifier: {value!r}")
    return value

def db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["PASSWORD"],
        database=None,
    )
