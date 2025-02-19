import os
import pytest
import psycopg2
import bcrypt
from dotenv import load_dotenv
from backend.accounts import register_user, authenticate, hash_password, verify_password

# `.env` 파일 로드
load_dotenv()

# 환경 변수에서 PostgreSQL 설정 직접 로드
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "sslmode": "require",
}

# 테스트용 아이디 및 비밀번호
TEST_USERNAME = "testuser01"
TEST_PASSWORD = "Test@123"

# PostgreSQL 테스트 데이터베이스 연결
@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    yield conn  # 테스트 실행
    conn.close()  # 테스트 종료 후 연결 닫기

# 비밀번호 해싱 테스트
def test_hash_password():
    hashed = hash_password(TEST_PASSWORD)
    assert isinstance(hashed, str)  # 해싱된 비밀번호는 문자열이어야 함
    assert bcrypt.checkpw(TEST_PASSWORD.encode(), hashed.encode())  # 원본 비밀번호와 비교

# 회원가입 테스트
def test_register_user(db_connection):
    success = register_user(TEST_USERNAME, TEST_PASSWORD)
    assert success is True  # 회원가입 성공 여부 확인

    # DB에서 사용자 조회하여 검증
    with db_connection.cursor() as cur:
        cur.execute("SELECT username FROM users WHERE username = %s", (TEST_USERNAME,))
        user = cur.fetchone()
    assert user is not None  # 사용자가 DB에 저장되었는지 확인

# 로그인 테스트 (올바른 비밀번호)
def test_authenticate_success():
    assert authenticate(TEST_USERNAME, TEST_PASSWORD) is True  # 인증 성공해야 함

# 로그인 테스트 (잘못된 비밀번호)
def test_authenticate_failure():
    assert authenticate(TEST_USERNAME, "WrongPassword") is False  # 인증 실패해야 함
