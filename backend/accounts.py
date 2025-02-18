import streamlit as st
import psycopg2
import bcrypt
from backend.config import DB_CONFIG

# PostgreSQL 연결 함수
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, sslmode="require")

# 비밀번호 해싱
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

# 비밀번호 검증
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# 사용자 등록
def register_user(username, password):
    hashed_password = hash_password(password)
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            return True  # 회원가입 성공
    except psycopg2.IntegrityError:
        return False  # 중복 아이디 오류

# 사용자 인증
def authenticate(username, password):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        user_data = cur.fetchone()
    
    if user_data:
        return verify_password(password, user_data[0])
    return False

# 로그인 처리 (세션 업데이트)
def login_user(username):
    st.session_state["authenticated"] = True
    st.session_state["user"] = username

# 로그아웃 처리
def logout():
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.info("📢 로그아웃 되었습니다.")
