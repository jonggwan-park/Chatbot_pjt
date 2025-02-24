import psycopg2
import bcrypt
import streamlit as st
from backend.db import get_connection, release_connection  # Connection Pool 활용


# 비밀번호 해싱
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


# 비밀번호 검증
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


# 사용자 등록
def register_user(username, password):
    """새 사용자를 데이터베이스에 추가"""
    hashed_password = hash_password(password)
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;",
                    (username, hashed_password),
                )
                conn.commit()
                return True  # 회원가입 성공
        except psycopg2.IntegrityError:
            return False  # 중복 아이디 오류
        finally:
            release_connection(conn)


# 사용자 인증 (로그인)
def authenticate(username, password):
    """사용자의 비밀번호를 검증하여 로그인 처리"""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT password FROM users WHERE username = %s AND is_active = TRUE",
                    (username,),
                )
                user_data = cur.fetchone()

            if user_data:
                return verify_password(password, user_data[0])  # 비밀번호 검증
            return False
        except Exception as e:
            print(f"Error during authentication: {e}")
            return False
        finally:
            release_connection(conn)


# 로그인 처리 (세션 업데이트)
def login_user(username):
    """로그인 시 세션에 사용자 정보 저장"""
    st.session_state["authenticated"] = True
    st.session_state["user"] = username
    st.success(f"{username}님, 로그인되었습니다.")


# 로그아웃 처리
def logout():
    """로그아웃 시 세션 초기화"""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.info("📢 로그아웃 되었습니다.")


# 회원 탈퇴 (is_active = False 로 변경)
def delete_user(username):
    """회원 탈퇴 시 실제 데이터를 삭제하는 대신 is_active = False로 변경"""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET is_active = FALSE WHERE username = %s",
                    (username,),
                )
                conn.commit()
                return True  # 탈퇴 성공
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            release_connection(conn)


# 로그인 상태 확인
def is_authenticated():
    """세션을 통해 현재 로그인 상태 확인"""
    return st.session_state.get("authenticated", False)
