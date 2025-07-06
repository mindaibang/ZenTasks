import streamlit as st
import matplotlib.pyplot as plt
from utils import *
from datetime import date

# Tạo bảng & admin mặc định
create_tables()
create_default_admin()

# Sidebar
st.sidebar.title("🔐 Login/Register")

if "page" not in st.session_state:
    st.session_state["page"] = "login"

if st.sidebar.button("📝 Register"):
    st.session_state["page"] = "register"

# Trang đăng ký
if st.session_state["page"] == "register":
    st.title("📝 Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    departments = get_departments()
    department = st.selectbox("Department", departments, format_func=lambda x: x[1])

    if st.button("Register"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, email, phone, role, department_id, approved)
                VALUES (?, ?, ?, ?, ?, 'member', ?, 0)
            """, (username, hash_password(password), full_name, email, phone, department[0]))
            conn.commit()
            st.success("🎉 Registered successfully! Wait for admin approval.")
            st.session_state["page"] = "login"
        except sqlite3.IntegrityError:
            st.error("⚠️ Username already exists.")
        conn.close()

# Trang đăng nhập
elif st.session_state["page"] == "login":
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = check_login(username, password)
        if user:
            user_id, role, approved, full_name = user
            if not approved:
                st.warning("⏳ Account not yet approved by Admin.")
            else:
                st.session_state["user_id"] = user_id
                st.session_state["role"] = role
                st.session_state["full_name"] = full_name
                st.session_state["page"] = "dashboard"
                st.experimental_rerun()
        else:
            st.error("❌ Wrong username or password.")

# Dashboard
elif st.session_state["page"] == "dashboard":
    st.sidebar.success(f"👤 {st.session_state['full_name']} ({st.session_state['role']})")
    st.title("📊 Dashboard")

    # Báo cáo tổng quan
    st.subheader("📈 Overall Task Summary")
    summary = get_tasks_summary()
    if summary:
        fig, ax = plt.subplots()
        ax.pie(summary.values(), labels=summary.keys(), autopct='%1.1f%%')
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.info("📭 No tasks yet.")

# Đăng xuất
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.experimental_rerun()
