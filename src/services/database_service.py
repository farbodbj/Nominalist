
import sqlite3
import os
from typing import List, Set
from contextlib import contextmanager

class DatabaseService:
    """Service for managing username database operations."""
    
    def __init__(self, db_path: str = "usernames.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the database with sample data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usernames (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add some sample existing usernames
            sample_usernames = [
                'john_doe', 'jane_smith', 'user123', 'admin', 'test_user',
                'muhammad_ali', 'ahmed123', 'jose_garcia', 'maria_lopez',
                'admin123', 'user_001', 'test123', 'sample_user'
            ]
            
            for username in sample_usernames:
                cursor.execute(
                    'INSERT OR IGNORE INTO usernames (username) VALUES (?)',
                    (username,)
                )
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def check_username_exists(self, username: str) -> bool:
        """Check if a username already exists in the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT 1 FROM usernames WHERE username = ? LIMIT 1',
                (username.lower(),)
            )
            return cursor.fetchone() is not None
    
    def check_multiple_usernames(self, usernames: List[str]) -> Set[str]:
        """Check multiple usernames and return set of existing ones."""
        existing = set()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join(['?' for _ in usernames])
            cursor.execute(
                f'SELECT username FROM usernames WHERE username IN ({placeholders})',
                [u.lower() for u in usernames]
            )
            existing.update(row[0] for row in cursor.fetchall())
        return existing
    
    def add_username(self, username: str):
        """Add a username to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO usernames (username) VALUES (?)',
                (username.lower(),)
            )
            conn.commit()
