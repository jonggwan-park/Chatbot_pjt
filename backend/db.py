import psycopg2
import streamlit as st
from psycopg2.extras import RealDictCursor

# Streamlit secrets.toml에서 DB 정보 가져오기
db_config = st.secrets["postgres"]

# PostgreSQL 연결 함수
def get_connection():
    return psycopg2.connect(
        dbname=db_config["POSTGRES_DB"],
        user=db_config["POSTGRES_USER"],
        password=db_config["POSTGRES_PASSWORD"],
        host=db_config["POSTGRES_HOST"],
        port=db_config["POSTGRES_PORT"],
        sslmode=db_config["SSL_MODE"],
        cursor_factory=RealDictCursor
    )

# 면접 기록 테이블 생성
def create_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS interview_records (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255),
                    question TEXT,
                    answer TEXT,
                    feedback TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

# 면접 기록 삽입
def insert_interview_record(user_id, question, answer, feedback):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO interview_records (user_id, question, answer, feedback)
                VALUES (%s, %s, %s, %s) RETURNING id;
            """, (user_id, question, answer, feedback))
            conn.commit()

# 사용자별 면접 기록 조회
def get_interview_records(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM interview_records WHERE user_id = %s ORDER BY timestamp DESC;", (user_id,))
            return cur.fetchall()
        
# 사용자별 면접 기록 조회 (필터링 지원)
def get_filtered_interview_records(user_id, role=None, start_date=None, end_date=None):
    query = "SELECT * FROM interview_records WHERE user_id = %s"
    params = [user_id]

    if role:
        query += " AND question LIKE %s"
        params.append(f"%{role}%")
    
    if start_date and end_date:
        query += " AND timestamp BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    query += " ORDER BY timestamp DESC"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            return cur.fetchall()
