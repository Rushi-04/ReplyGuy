"""
Database - Tracks replied tweets to avoid duplicates
"""
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "session" / "replied_tweets.db"


class Database:
    """Manages database of replied tweets"""
    
    def __init__(self):
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create table if needed"""
        try:
            DB_PATH.parent.mkdir(exist_ok=True)
            self.conn = sqlite3.connect(str(DB_PATH))
            cursor = self.conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS replied_tweets (
                    tweet_id TEXT PRIMARY KEY,
                    username TEXT,
                    tweet_text TEXT,
                    reply_text TEXT,
                    replied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    def has_replied(self, tweet_id: str) -> bool:
        """Check if we've already replied to this tweet"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1 FROM replied_tweets WHERE tweet_id = ?", (tweet_id,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking reply status: {e}")
            return False
    
    def mark_replied(self, tweet_id: str, username: str, tweet_text: str, reply_text: str):
        """Mark a tweet as replied to"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO replied_tweets 
                (tweet_id, username, tweet_text, reply_text, replied_at)
                VALUES (?, ?, ?, ?, ?)
            """, (tweet_id, username, tweet_text, reply_text, datetime.now()))
            self.conn.commit()
            logger.info(f"Marked tweet {tweet_id} as replied")
        except Exception as e:
            logger.error(f"Error marking tweet as replied: {e}")
    
    def get_replied_count(self) -> int:
        """Get total number of replied tweets"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM replied_tweets")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting replied count: {e}")
            return 0
    
    def get_recent_replies(self, limit: int = 10) -> List[dict]:
        """Get recent replies"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT tweet_id, username, tweet_text, reply_text, replied_at
                FROM replied_tweets
                ORDER BY replied_at DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [
                {
                    'tweet_id': row[0],
                    'username': row[1],
                    'tweet_text': row[2],
                    'reply_text': row[3],
                    'replied_at': row[4]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error getting recent replies: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

