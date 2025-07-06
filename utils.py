import sqlite3
import hashlib
from datetime import datetime

DB_FILE = "database.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def create_tables():
    conn = get_connection()
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.role, u.approved, u.full_name, d.name AS department
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE u.username=? AND u.password_hash=?
    """, (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user  # (id, role, approved, full_name, department) or None

def get_departments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM departments")
    departments = cursor.fetchall()
    conn.close()
    return departments

def add_department(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO departments (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Ignore if already exists
    conn.close()

def get_pending_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, email FROM users WHERE approved=0")
    users = cursor.fetchall()
    conn.close()
    return users

def approve_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET approved=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.username, u.role, d.name AS department
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE u.approved=1
    """)
    users = cursor.fetchall()
    conn.close()
    return users

def add_task(title, description, priority, start_date, due_date, assigned_to, created_by, department_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, description, priority, start_date, due_date, assigned_to, created_by, department_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, description, priority, start_date, due_date, assigned_to, created_by, department_id))
    conn.commit()
    conn.close()

def get_tasks_summary(department_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if department_id:
        cursor.execute("""
            SELECT status, COUNT(*) FROM tasks WHERE department_id=? GROUP BY status
        """, (department_id,))
    else:
        cursor.execute("""
            SELECT status, COUNT(*) FROM tasks GROUP BY status
        """)
    summary = cursor.fetchall()
    conn.close()
    return dict(summary)
