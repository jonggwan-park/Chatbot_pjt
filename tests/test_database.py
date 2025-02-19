import os
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from backend.db import (
    get_connection,
    create_tables,
    insert_interview_record,
    get_interview_records,
    get_filtered_interview_records,
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
    "sslmode": os.getenv("SSL_MODE"),
}

# 테스트용 데이터
TEST_USER_ID = "test_user"
TEST_QUESTION = "What is PostgreSQL?"
TEST_ANSWER = "PostgreSQL is an open-source relational database."
TEST_FEEDBACK = "Good answer, but add more details about ACID properties."

# PostgreSQL 연결 테스트
@pytest.fixture(scope="module")
def db_connection():
    """데이터베이스 연결을 설정하고 테스트 후 정리"""
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    yield conn
    conn.close()

# 테이블 생성 테스트
@pytest.fixture(autouse=True)
def setup_and_teardown(db_connection):
    """테스트 실행 전 테이블 생성, 실행 후 데이터 정리"""
    with db_connection.cursor() as cur:
        create_tables()  # 테이블이 존재하는지 확인
        cur.execute("DELETE FROM interview_records WHERE user_id = %s", (TEST_USER_ID,))
        db_connection.commit()  # 삭제 후 커밋

        # 테스트 실행 전에 기본 테스트 데이터를 삽입하고 커밋
        cur.execute("""
            INSERT INTO interview_records (user_id, question, answer, feedback)
            VALUES (%s, %s, %s, %s);
        """, (TEST_USER_ID, TEST_QUESTION, TEST_ANSWER, TEST_FEEDBACK))
        db_connection.commit()  # 커밋

    yield  # 테스트 실행

    with db_connection.cursor() as cur:
        cur.execute("DELETE FROM interview_records WHERE user_id = %s", (TEST_USER_ID,))
        db_connection.commit()  # ✅ 테스트 종료 후 데이터 정리


# 면접 기록 삽입 테스트
def test_insert_interview_record():
    insert_interview_record(TEST_USER_ID, TEST_QUESTION, TEST_ANSWER, TEST_FEEDBACK)

    records = get_interview_records(TEST_USER_ID)
    assert len(records) > 0  # 데이터가 정상적으로 삽입되었는지 확인
    assert records[0]["question"] == TEST_QUESTION
    assert records[0]["answer"] == TEST_ANSWER
    assert records[0]["feedback"] == TEST_FEEDBACK

# 사용자별 면접 기록 조회 테스트
def test_get_interview_records():
    records = get_interview_records(TEST_USER_ID)
    assert isinstance(records, list)  # 반환 값이 리스트인지 확인
    assert len(records) > 0  # 데이터가 존재하는지 확인
    assert records[0]["user_id"] == TEST_USER_ID  # 올바른 사용자 데이터인지 확인

# 필터링된 면접 기록 조회 테스트
def test_get_filtered_interview_records():
    filtered_records = get_filtered_interview_records(TEST_USER_ID, role="PostgreSQL")
    
    assert isinstance(filtered_records, list)
    assert len(filtered_records) > 0  # 필터링된 데이터가 존재하는지 확인
    assert "PostgreSQL" in filtered_records[0]["question"]  # 질문 내용에 PostgreSQL 포함
