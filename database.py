import sqlite3
import hashlib
import streamlit as st  

@st.cache_data(ttl=60)
def get_all_events():
    conn = get_connnection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, organizer_username, activity_type, location, event_date, description FROM events ORDER BY id DESC")
    events = cursor.fetchall()
    conn.close()
    return events

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
            organizer_username TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            location TEXT NOT NULL,
            event_date TEXT NOT NULL,
            description TEXT
        )
    """)
    
    # Unified Event Registrations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_title TEXT NOT NULL,
            username TEXT NOT NULL,
            full_name TEXT,
            dob TEXT,
            age INTEGER,
            email TEXT,
            phone TEXT,
            residence TEXT,
            parent_name TEXT,
            parent_contact TEXT,
            parent_email TEXT
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
            """INSERT INTO users (username, password_hash, role) 
            VALUES (?, ?, ?)""",
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
      VALUES (?, ?, ?, ?, ?, ?)""", 
      (title, organizer_username, activity_type, location, str(event_date), description)
    )
    conn.commit()
    conn.close()

def get_ngo_events(organizer_username):
    conn = get_connnection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, activity_type, location, event_date, description FROM events WHERE organizer_username = ?", (organizer_username,))
    events = cursor.fetchall()
    conn.close()
    return events

def register_volunteer(event_title, username, full_name, email, dob,age, parent_name, parent_contact, parent_email):
    conn = get_connnection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO event_registrations 
        (event_title, username, full_name, email, dob,age, parent_name, parent_contact, parent_email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
    """, (event_title, username, full_name, email, str(dob), age,parent_name, parent_contact, parent_email))
    conn.commit()
    conn.close()
    return True

def get_event_volunteers(event_title):
    conn = get_connnection()
    cursor = conn.cursor()
    # Make sure event_title is passed as a string, not a tuple
    if isinstance(event_title, tuple):
        event_title = event_title[0]

    cursor.execute("""
        SELECT full_name, email, dob, age, parent_name, parent_contact, parent_email
        FROM event_registrations
        WHERE event_title = ?
    """, (str(event_title),))
    volunteers = cursor.fetchall()
    conn.close()
    return volunteers

def get_user_registered_events(username):
    conn = get_connnection()
    cursor = conn.cursor()
    # Join event_registrations with events to get full details of registered events
    cursor.execute("""
        SELECT e.title, e.organizer_username, e.activity_type, e.location, e.event_date, e.description
        FROM events e
        INNER JOIN event_registrations r ON e.title = r.event_title
        WHERE r.username = ?
        ORDER BY e.event_date ASC
    """, (username,))
    events = cursor.fetchall()
    conn.close()
    return events