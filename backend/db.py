# test용 코드

import streamlit as st
from sqlalchemy import create_engine, text

# PostgreSQL 연결 정보 불러오기
DB_USER = st.secrets["postgres"]["POSTGRES_USER"]
DB_PASSWORD = st.secrets["postgres"]["POSTGRES_PASSWORD"]
DB_HOST = st.secrets["postgres"]["POSTGRES_HOST"]
DB_PORT = st.secrets["postgres"]["POSTGRES_PORT"]
DB_NAME = st.secrets["postgres"]["POSTGRES_DB"]
SSL_MODE = st.secrets["postgres"]["SSL_MODE"]

# SQLAlchemy 엔진 생성 (SSL 모드 적용)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={SSL_MODE}"
engine = create_engine(DATABASE_URL)

def insert_chat_message(user_message, ai_response):
    """사용자의 메시지와 AI 응답을 PostgreSQL에 저장"""
    with engine.connect() as connection:
        query = text("INSERT INTO chat_logs (user_message, ai_response) VALUES (:user_message, :ai_response)")
        connection.execute(query, {"user_message": user_message, "ai_response": ai_response})
        connection.commit() 


def get_chat_history():
    """대화 기록을 DB에서 불러오기"""
    with engine.connect() as connection:
        query = text("SELECT user_message, ai_response FROM chat_logs ORDER BY id DESC LIMIT 10")
        result = connection.execute(query).fetchall()
        return result
