import hashlib
import secrets
from sqlite3 import connect
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
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (account, password, token) VALUES (?, ?, ?)",
                (account, encode(password),
                 token := f"{id}{datetime.now().strftime('%Y%m%d')}{secrets.token_urlsafe(32)}")
            )
            conn.commit()
            return token

    def login_and_get_token(self, account: str, password: str) -> str:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, token FROM users WHERE account = ? AND password = ?",
                (account, encode(password))
            )
            user_id = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE users SET token = ? WHERE id = ?",
                (token := f"{user_id}{datetime.now().strftime('%Y%m%d%H%M%S')}{secrets.token_urlsafe(32)}", user_id)
            )
            conn.commit()
            return token

    def check_if_token_exist(self, token: str) -> bool:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT token FROM users WHERE token = ?", (token,))
            return cursor.fetchone() is not None

    def add_email_and_cred(self, token: str, email: str, credential: str) -> None:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO emails (user_id, email, credential) VALUES (?, ?, ?)",
                (token, email, credential)
            )
            conn.commit()

    def update_cred_by_email(self, credential: str, email: str) -> None:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE emails SET credential = ? WHERE email = ?",
                (credential, email)
            )
            conn.commit()

    def get_all_cred_by_token(self, token: str) -> list[tuple[str, str]]:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT emails.email, emails.credential FROM emails "
                "JOIN users ON emails.user_id = users.id WHERE users.token = ?",
                (token,)
            )
            return cursor.fetchall()
