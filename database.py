import sqlite3
import hashlib

def get_connnection():
    return sqlite3.connect("ocean_connect,db")
def init_db():
    #creates the users table if it not already present
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
      CREATE TAABLE IF NOT EXISTS user(
      id INTEGER PRIAMRY KEY AUTOINCREMENT,
      username TEST UNIQUE NOT NULL,
      password_hash TEXT NOT NULL) """
    )