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

    def sign_up(self, account: str, password: str) -> None:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (account, password) VALUES (?, ?)",
                (account, encode(password))
            )
            conn.commit()

    def login_and_get_session(self, account: str, password: str) -> str:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE account = ? AND password = ?",
                (account, encode(password))
            )
            user_id = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE users SET session = ? WHERE id = ?",
                (session := f"{user_id}{datetime.now().strftime('%Y%m%d%H%M%S')}{secrets.token_urlsafe(32)}", user_id)
            )
            conn.commit()
            return session

    def get_account_by_session(self, session: str) -> str:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT account FROM users WHERE session = ?", (session,))
            return cursor.fetchone()[0]

    def check_if_session_exist(self, session: str) -> bool:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT session FROM users WHERE session = ?", (session,))
            return cursor.fetchone() is not None

    def add_email_and_cred(self, session: str, email: str, credential: str) -> None:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE session = ? AND email = ?", (session, email))
            if cursor.fetchone() is not None:
                return
            cursor.execute("SELECT id FROM users WHERE session = ?", (session,))
            user_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO emails (user_id, email, credential) VALUES (?, ?, ?)",
                (user_id, email, credential)
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

    def get_all_cred_by_session(self, session: str) -> list[tuple[str, str]]:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT emails.email, emails.credential FROM emails "
                "JOIN users ON emails.user_id = users.id WHERE users.session = ? "
                "ORDER BY emails.id",
                (session,)
            )
            return cursor.fetchall()

    def get_all_cred_by_account(self, account: str) -> list[tuple[str, str]]:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT emails.email, emails.credential FROM emails "
                "JOIN users ON emails.user_id = users.id WHERE users.account = ? "
                "ORDER BY emails.id",
                (account,)
            )
            return cursor.fetchall()

    def get_first_email_by_account(self, account: str) -> str:
        with connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT emails.email FROM emails "
                "JOIN users ON emails.user_id = users.id WHERE users.account = ? "
                "ORDER BY emails.id",
                (account,)
            )
            return cursor.fetchone()[0]
