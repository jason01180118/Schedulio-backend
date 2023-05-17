import hashlib
import sqlite3


def encode(password):
    sha256_hash = hashlib.sha256()
    password_bytes = password.encode("utf-8")
    sha256_hash.update(password_bytes)
    return sha256_hash.hexdigest()


class Database:
    def __init__(self, db):
        self.db = db

    def add_user_and_get_id(self, account, password):
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (account, password) VALUES (?, ?);",
                (account, encode(password))
            )
            conn.commit()
            return cursor.lastrowid

    def login_and_get_id(self, account, password):
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE account=? AND password=?;",
                (account, encode(password))
            )
            user = cursor.fetchone()
            return user[0]
