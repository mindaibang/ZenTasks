import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import *
from datetime import date

# Tạo bảng nếu chưa có
create_tables()

# ----------------- Sidebar -----------------
st.sidebar.title("🔐 Đăng nhập / Đăng ký")

if "page" not in st.session_state:
    st.session_state["page"] = "login"

if st.sidebar.button("📝 Đăng ký tài khoản"):
    st.session_state["page"] = "register"

# ----------------- Trang đăng ký -----------------
if st.session_state["page"] == "register":
    st.title("📝 Đăng ký tài khoản")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    full_name = st.text_input("Họ tên")
    email = st.text_input("Email")
    phone = st.text_input("Số điện thoại")
    departments = get_departments()
    department = st.selectbox("Phòng ban", departments, format_func=lambda x: x[1])

    if st.button("Đăng ký"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, email, phone, role, department_id, approved) 
                VALUES (?, ?, ?, ?, ?, 'member', ?, 0)
            """, (username, hash_password(password), full_name, email, phone, department[0]))
            conn.commit()
            st.success("🎉 Đăng ký thành công! Chờ Admin phê duyệt.")
            st.session_state["page"] = "login"
        except sqlite3.IntegrityError:
            st.error("⚠️ Username đã tồn tại.")
        conn.close()

# ----------------- Trang đăng nhập -----------------
elif st.session_state["page"] == "login":
    st.title("🔐 Đăng nhập")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Đăng nhập"):
        user = check_login(username, password)
        if user:
            user_id, role, approved, full_name, department = user
            if not approved:
                st.warning("⏳ Tài khoản chưa được Admin phê duyệt.")
            else:
                st.session_state["user_id"] = user_id
                st.session_state["role"] = role
                st.session_state["full_name"] = full_name
                st.session_state["department"] = department
                st.session_state["page"] = "dashboard"
                st.experimental_rerun()
        else:
            st.error("❌ Sai username hoặc password.")

# ----------------- Dashboard -----------------
elif st.session_state["page"] == "dashboard":
    role = st.session_state["role"]
    user_id = st.session_state["user_id"]
    st.sidebar.success(f"👤 {st.session_state['full_name']} ({role.capitalize()})")

    if role == "admin":
        st.title("👑 Trang Admin")

        # Quản lý phòng ban
        st.subheader("🏢 Quản lý phòng ban")
        new_dept = st.text_input("➕ Thêm phòng ban mới")
        if st.button("Thêm phòng ban"):
            add_department(new_dept)
            st.success(f"✅ Đã thêm phòng ban: {new_dept}")
            st.experimental_rerun()

        st.write("📋 Danh sách phòng ban:")
        for dept in get_departments():
            st.write(f"- {dept[1]}")

        # Báo cáo tổng quan
        st.subheader("📊 Báo cáo tổng quan")
        summary = get_tasks_summary()
        labels = summary.keys()
        sizes = summary.values()
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.axis('equal')
        st.pyplot(fig)

# ----------------- Logout -----------------
if st.sidebar.button("🚪 Đăng xuất"):
    st.session_state.clear()
    st.experimental_rerun()
