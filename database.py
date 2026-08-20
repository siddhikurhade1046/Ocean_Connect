import sqlite3
import hashlib

def get_connnection():
    return sqlite3.connect("ocean_connect.db")

def init_db():
    conn = get_connnection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    
    # Create events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ngo_username TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, password: str, role: str) -> bool:
    conn = get_connnection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str):
    conn = get_connnection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash, role FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()

    if result and result[0] == hash_password(password):
        return result[1]
    return None

def add_event(title, organizer_username, activity_type, location, event_date, description):
     conn = get_connnection()      
     cursor = conn.cursor()
     cursor.execute(""" 
      INSERT INTO events (title, organizer_username, activity_type, location, event_date, description)
      VALUES (?, ?, ?, ?, ?, ?)""",(title , organizer_username, activity_type, location, str(event_date), description))
     conn.commit()
     conn.close()

def get_all_events():
    conn = get_connnection()
    cursor = conn.cursor()
    cursor.execute("SELECET title, organizer_username, activity_type, location, event_date,description FROM events ORDER BY id DESC")
    events = cursor.fetchall()
    conn.close()
    return events

def get_organizer_events(organizer_username):
    conn = get_connnection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, activity_type, location, event_date, description FROM events WHERE organizer_username = ?",(organizer_username,))
    events = cursor.fetchall()
    conn.close()
    return events
     