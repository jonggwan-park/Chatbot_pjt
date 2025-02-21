import os
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from backend.db import (
    create_chat_session,
    insert_chat_message,
    get_chat_history,
    get_user_chat_sessions,
    delete_chat_messages,    # 추가
    delete_chat_session,     # 추가
    delete_all_user_sessions # 추가
)

# `.env` 파일 로드 (Streamlit secrets.toml 대신 직접 환경 변수 사용)
load_dotenv()

# PostgreSQL 테스트 데이터베이스 설정 (환경 변수에서 로드)
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "sslmode": os.getenv("SSL_MODE", "require"),
}

# 테스트용 데이터
TEST_USER_ID = 1  # 실제 users 테이블에 테스트용 사용자 ID 필요
TEST_MESSAGE_USER = "Hello, chatbot!"
TEST_MESSAGE_BOT = "Hello! How can I help you?"

# PostgreSQL 연결 테스트
@pytest.fixture(scope="module")
def db_connection():
    """데이터베이스 연결을 설정하고 테스트 후 정리"""
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    yield conn
    conn.close()

# 테스트 데이터 정리 및 설정 (복원된 코드)
@pytest.fixture(autouse=True)
def setup_and_teardown(db_connection):
    """테스트 실행 전 데이터 정리 및 설정"""
    with db_connection.cursor() as cur:
        # 기존 테스트 데이터 삭제
        cur.execute("DELETE FROM chat_messages WHERE session_id IN (SELECT id FROM chat_sessions WHERE user_id = %s);", (TEST_USER_ID,))
        cur.execute("DELETE FROM chat_sessions WHERE user_id = %s;", (TEST_USER_ID,))
        db_connection.commit()

        # 새로운 채팅 세션 생성
        cur.execute("INSERT INTO chat_sessions (user_id) VALUES (%s) RETURNING id;", (TEST_USER_ID,))
        session_id = cur.fetchone()["id"]
        db_connection.commit()

        # 테스트 메시지 삽입
        cur.execute("INSERT INTO chat_messages (session_id, sender, message) VALUES (%s, %s, %s);",
                    (session_id, "user", TEST_MESSAGE_USER))
        cur.execute("INSERT INTO chat_messages (session_id, sender, message) VALUES (%s, %s, %s);",
                    (session_id, "bot", TEST_MESSAGE_BOT))
        db_connection.commit()

    yield  # 테스트 실행

    with db_connection.cursor() as cur:
        cur.execute("DELETE FROM chat_messages WHERE session_id IN (SELECT id FROM chat_sessions WHERE user_id = %s);", (TEST_USER_ID,))
        cur.execute("DELETE FROM chat_sessions WHERE user_id = %s;", (TEST_USER_ID,))
        db_connection.commit()

# 채팅 세션 생성 테스트
def test_create_chat_session():
    """사용자가 새 채팅 세션을 생성할 수 있는지 테스트"""
    session_id = create_chat_session(TEST_USER_ID)
    assert session_id is not None  # 세션 ID가 정상적으로 반환되는지 확인

# 채팅 메시지 삽입 테스트
def test_insert_chat_message():
    """채팅 세션에 사용자 및 챗봇 메시지가 정상적으로 저장되는지 확인"""
    session_id = create_chat_session(TEST_USER_ID)
    insert_chat_message(session_id, "user", TEST_MESSAGE_USER)
    insert_chat_message(session_id, "bot", TEST_MESSAGE_BOT)

    # 대화 내역 조회
    chat_history = get_chat_history(session_id)
    assert len(chat_history) == 2  # 두 개의 메시지가 저장되었는지 확인
    assert chat_history[0]["sender"] == "user" and chat_history[0]["message"] == TEST_MESSAGE_USER
    assert chat_history[1]["sender"] == "bot" and chat_history[1]["message"] == TEST_MESSAGE_BOT

# 특정 채팅 세션의 대화 내역 조회 테스트
def test_get_chat_history():
    """특정 채팅 세션의 대화 기록을 시간순으로 조회할 수 있는지 확인"""
    session_id = create_chat_session(TEST_USER_ID)
    insert_chat_message(session_id, "user", "Test message 1")
    insert_chat_message(session_id, "bot", "Test response 1")
    insert_chat_message(session_id, "user", "Test message 2")
    insert_chat_message(session_id, "bot", "Test response 2")

    chat_history = get_chat_history(session_id)
    assert len(chat_history) == 4  # 네 개의 메시지가 저장되었는지 확인
    assert chat_history[0]["message"] == "Test message 1"
    assert chat_history[1]["message"] == "Test response 1"
    assert chat_history[2]["message"] == "Test message 2"
    assert chat_history[3]["message"] == "Test response 2"

# 사용자의 모든 채팅 세션 조회 테스트
def test_get_user_chat_sessions():
    """사용자가 가진 모든 채팅 세션 목록을 가져올 수 있는지 테스트"""
    create_chat_session(TEST_USER_ID)  # 세션 하나 추가 생성
    sessions = get_user_chat_sessions(TEST_USER_ID)
    assert isinstance(sessions, list)  # 반환 값이 리스트인지 확인
    assert len(sessions) > 0  # 세션이 하나 이상 존재해야 함
    assert "id" in sessions[0] and "created_at" in sessions[0]  # 세션 데이터 구조 확인

# 특정 세션의 채팅 메시지 삭제 테스트
def test_delete_chat_messages():
    """특정 채팅 세션의 모든 메시지를 삭제할 수 있는지 테스트"""
    session_id = create_chat_session(TEST_USER_ID)
    insert_chat_message(session_id, "user", "Test message")
    insert_chat_message(session_id, "bot", "Test response")

    # 삭제 실행
    delete_chat_messages(session_id)

    # 데이터가 삭제되었는지 확인
    chat_history = get_chat_history(session_id)
    assert len(chat_history) == 0  # 모든 메시지가 삭제되었어야 함

# 특정 채팅 세션 및 모든 메시지 삭제 테스트
def test_delete_chat_session():
    """특정 채팅 세션과 모든 메시지를 삭제할 수 있는지 테스트"""
    session_id = create_chat_session(TEST_USER_ID)
    insert_chat_message(session_id, "user", "Test message")
    insert_chat_message(session_id, "bot", "Test response")

    # 세션 삭제 실행
    delete_chat_session(session_id)

    # 메시지와 세션이 삭제되었는지 확인
    chat_history = get_chat_history(session_id)
    assert len(chat_history) == 0  # 메시지가 삭제되었어야 함

    # 사용자의 세션 조회
    sessions = get_user_chat_sessions(TEST_USER_ID)
    assert session_id not in [s["id"] for s in sessions]  # 세션 ID가 목록에 없어야 함

# 특정 사용자의 모든 채팅 데이터 삭제 테스트
def test_delete_all_user_sessions():
    """특정 사용자의 모든 채팅 세션과 관련 메시지를 삭제할 수 있는지 테스트"""
    session1 = create_chat_session(TEST_USER_ID)
    session2 = create_chat_session(TEST_USER_ID)
    
    insert_chat_message(session1, "user", "Session 1 - Message")
    insert_chat_message(session2, "user", "Session 2 - Message")

    delete_all_user_sessions(TEST_USER_ID)

    sessions = get_user_chat_sessions(TEST_USER_ID)
    assert len(sessions) == 0  # 사용자의 모든 세션이 삭제되었어야 함

    assert len(get_chat_history(session1)) == 0
    assert len(get_chat_history(session2)) == 0
