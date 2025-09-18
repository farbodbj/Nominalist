import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from typing import List, Set


class DatabaseService:
    """Service for managing username database operations using MariaDB/MySQL."""

    def __init__(
        self,
        host: str = "localhost",
        user: str = "root",
        password: str = "",
        database: str = "usernames_db",
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self._initialize_db()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_db(self):
        """Initialize the database and create table if not exists."""
        try:
            # Ensure database exists
            conn = mysql.connector.connect(
                host=self.host, user=self.user, password=self.password
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            conn.commit()
            conn.close()

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.database}.usernames (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                # Sample usernames
                sample_usernames = [
                    "john_doe",
                    "jane_smith",
                    "user123",
                    "admin",
                    "test_user",
                    "muhammad_ali",
                    "ahmed123",
                    "jose_garcia",
                    "maria_lopez",
                    "admin123",
                    "user_001",
                    "test123",
                    "sample_user",
                ]

                for username in sample_usernames:
                    cursor.execute(
                        "INSERT IGNORE INTO usernames (username) VALUES (%s)",
                        (username.lower(),),
                    )

                conn.commit()
        except Error as e:
            print(f"Database initialization error: {e}")

    def check_username_exists(self, username: str) -> bool:
        """Check if a username already exists in the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM usernames WHERE username = %s LIMIT 1",
                (username.lower(),),
            )
            return cursor.fetchone() is not None

    def check_multiple_usernames(self, usernames: List[str]) -> Set[str]:
        """Check multiple usernames and return set of existing ones."""
        if not usernames:
            return set()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["%s"] * len(usernames))
            cursor.execute(
                f"SELECT username FROM usernames WHERE username IN ({placeholders})",
                [u.lower() for u in usernames],
            )
            return {row[0] for row in cursor.fetchall()}

    def add_username(self, username: str):
        """Add a username to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT IGNORE INTO usernames (username) VALUES (%s)",
                (username.lower(),),
            )
            conn.commit()
