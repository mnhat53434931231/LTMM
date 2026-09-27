import sqlite3
from config import DB_PATH #import db
    
def get_connection():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON'); return conn

def init_db():
    with get_connection() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, public_key_path TEXT NOT NULL, private_key_path TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wallets(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE NOT NULL, balance REAL NOT NULL DEFAULT 0, FOREIGN KEY(user_id) REFERENCES users(id));
        CREATE TABLE IF NOT EXISTS transactions(id TEXT PRIMARY KEY, sender_id INTEGER NOT NULL, receiver_id INTEGER NOT NULL, amount REAL NOT NULL, timestamp TEXT NOT NULL, transaction_hash TEXT NOT NULL, signature TEXT NOT NULL, status TEXT NOT NULL, FOREIGN KEY(sender_id) REFERENCES users(id), FOREIGN KEY(receiver_id) REFERENCES users(id));
        ''')
def fetch_one(q,p=()):
    with get_connection() as c: return c.execute(q,p).fetchone()
def fetch_all(q,p=()):
    with get_connection() as c: return c.execute(q,p).fetchall()
