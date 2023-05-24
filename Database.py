import hashlib
import secrets
import sqlite3
from datetime import datetime


def encode(password: str) -> str:
    sha256_hash = hashlib.sha256()
    password_bytes = password.encode("utf-8")
    sha256_hash.update(password_bytes)
    return sha256_hash.hexdigest()


class Database:
    def __init__(self, db: str):
        self.db = db

    def sign_up_and_get_token(self, account: str, password: str) -> str:
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (account, password, token) VALUES (?, ?, ?)",
                (account, encode(password), token := f'{id}{datetime.now().strftime("%Y%m%d")}{secrets.token_urlsafe(32)}')
            )
            conn.commit()
            return token

    def login_and_get_token(self, account: str, password: str) -> str:
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, token FROM users WHERE account=? AND password=?",
                (account, encode(password))
            )
            user_id = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE users SET token=? WHERE id=?",
                (token := f'{id}{datetime.now().strftime("%Y%m%d")}{secrets.token_urlsafe(32)}', user_id)
            )
            return token

    def check_if_token_exist(self, token: str) -> bool:
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT token FROM users WHERE token=?", (token,))
            return cursor.fetchone() is not None
