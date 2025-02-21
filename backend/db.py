import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import streamlit as st
from backend.config import DB_CONFIG  # `config.py`에서 DB 설정 가져오기

# Connection Pool 생성 (최소 1개, 최대 5개)
try:
    connection_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=5,
        dbname=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        sslmode=st.secrets["postgres"].get("SSL_MODE", "require")  # 기본값 'require'
    )
    if connection_pool:
        print("Database connection pool created successfully.")
except Exception as e:
    print(f"Database connection pool creation failed: {e}")

# PostgreSQL 연결 함수 (연결 풀에서 가져오기)
def get_connection():
    try:
        return connection_pool.getconn()
    except Exception as e:
        print(f"Error getting connection from pool: {e}")
        return None

# 연결 반환 함수
def release_connection(conn):
    if conn:
        connection_pool.putconn(conn)

# 새로운 채팅 세션 생성
def create_chat_session(user_id):
    """새로운 채팅 세션을 생성하고, 세션 ID를 반환"""
    conn = get_connection()
    session_id = None
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO chat_sessions (user_id) VALUES (%s) RETURNING id;", (user_id,))
                session_id = cur.fetchone()[0]
                conn.commit()
        except Exception as e:
            print(f"Error creating chat session: {e}")
        finally:
            release_connection(conn)
    return session_id

# 챗봇과의 대화 메시지 삽입
def insert_chat_message(session_id, sender, message):
    """사용자 또는 챗봇이 보낸 메시지를 저장"""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO chat_messages (session_id, sender, message) 
                    VALUES (%s, %s, %s);
                """, (session_id, sender, message))
                conn.commit()
        except Exception as e:
            print(f"Error inserting chat message: {e}")
        finally:
            release_connection(conn)

# 특정 세션의 대화 내역 가져오기
def get_chat_history(session_id):
    """특정 채팅 세션의 대화 내역을 시간순으로 조회"""
    conn = get_connection()
    chat_history = []
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT sender, message, timestamp 
                    FROM chat_messages 
                    WHERE session_id = %s 
                    ORDER BY timestamp ASC;
                """, (session_id,))
                chat_history = cur.fetchall()
        except Exception as e:
            print(f"Error fetching chat history: {e}")
        finally:
            release_connection(conn)
    return chat_history

# 사용자별 전체 채팅 세션 목록 가져오기
def get_user_chat_sessions(user_id):
    """사용자가 가진 모든 채팅 세션을 최신순으로 조회"""
    conn = get_connection()
    sessions = []
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, created_at 
                    FROM chat_sessions 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC;
                """, (user_id,))
                sessions = cur.fetchall()
        except Exception as e:
            print(f"Error fetching chat sessions: {e}")
        finally:
            release_connection(conn)
    return sessions

# 전체 사용자 대화 기록 조회
def get_all_chat_sessions():
    """모든 사용자 채팅 세션 목록을 최신순으로 조회"""
    conn = get_connection()
    sessions = []
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT cs.id, u.username, cs.created_at 
                    FROM chat_sessions cs
                    JOIN users u ON cs.user_id = u.id
                    ORDER BY cs.created_at DESC;
                """)
                sessions = cur.fetchall()
        except Exception as e:
            print(f"Error fetching all chat sessions: {e}")
        finally:
            release_connection(conn)
    return sessions

# 특정 채팅 세션의 대화 메시지 삭제
def delete_chat_messages(session_id):
    """특정 채팅 세션의 모든 메시지를 삭제"""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM chat_messages WHERE session_id = %s;", (session_id,))
                conn.commit()
                print(f"Chat messages for session {session_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting chat messages: {e}")
        finally:
            release_connection(conn)

# 특정 채팅 세션과 모든 대화 내역 삭제
def delete_chat_session(session_id):
    """특정 채팅 세션의 메시지와 세션 정보를 삭제"""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # 1. 먼저 해당 세션의 메시지 삭제
                cur.execute("DELETE FROM chat_messages WHERE session_id = %s;", (session_id,))
                # 2. 채팅 세션 삭제
                cur.execute("DELETE FROM chat_sessions WHERE id = %s;", (session_id,))
                conn.commit()
                print(f"Chat session {session_id} and its messages deleted successfully.")
        except Exception as e:
            print(f"Error deleting chat session: {e}")
        finally:
            release_connection(conn)

# 특정 사용자의 모든 채팅 세션 및 대화 삭제
def delete_all_user_sessions(user_id):
    """특정 사용자의 모든 채팅 세션과 연관된 메시지를 삭제"""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # 1. 사용자의 모든 세션 ID 조회
                cur.execute("SELECT id FROM chat_sessions WHERE user_id = %s;", (user_id,))
                sessions = cur.fetchall()
                
                # 2. 각 세션의 메시지 삭제
                for session in sessions:
                    cur.execute("DELETE FROM chat_messages WHERE session_id = %s;", (session[0],))
                
                # 3. 사용자의 모든 세션 삭제
                cur.execute("DELETE FROM chat_sessions WHERE user_id = %s;", (user_id,))
                conn.commit()
                print(f"All chat sessions and messages for user {user_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting all user chat sessions: {e}")
        finally:
            release_connection(conn)