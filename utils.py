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

def create_default_admin():
    conn = get_connection()
    cursor = conn.cursor()
    # Kiểm tra xem đã có user admin chưa
    cursor.execute("SELECT * FROM users WHERE role='admin'")
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, email, phone, role, approved)
            VALUES (?, ?, ?, ?, ?, 'admin', 1)
        """, (
            'admin',  # username
            hash_password('admin123'),  # password mặc định
            'Default Admin',
            'admin@example.com',
            '0000000000'
        ))
        conn.commit()
        print("✅ Đã tạo admin mặc định: username=admin, password=admin123")
    else:
        print("✅ Admin đã tồn tại, bỏ qua tạo mặc định.")
    conn.close()

def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.role, u.approved, u.full_name
        FROM users u
        WHERE u.username=? AND u.password_hash=?
    """, (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user  # (id, role, approved, full_name) or None

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
        pass  # Ignore nếu đã tồn tại
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

def get_tasks_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status, COUNT(*) FROM tasks GROUP BY status
    """)
    summary = cursor.fetchall()
    conn.close()
    return dict(summary)
