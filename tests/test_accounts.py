import os
import pytest
import psycopg2
import bcrypt
from dotenv import load_dotenv
from backend.accounts import register_user, authenticate, hash_password, verify_password, delete_user

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

# PostgreSQL 테스트 데이터베이스 연결 (pytest fixture)
@pytest.fixture(scope="module")
def db_connection():
    """테스트용 DB 연결을 제공하는 pytest fixture"""
    conn = psycopg2.connect(**DB_CONFIG)  # `.env`에서 로드한 DB 정보로 직접 연결
    yield conn  # 테스트 실행
    conn.rollback()  # 테스트 후 변경사항 롤백
    conn.close()  # 연결 닫기

# 비밀번호 해싱 테스트
def test_hash_password():
    """비밀번호 해싱 및 검증 테스트"""
    hashed = hash_password(TEST_PASSWORD)
    assert isinstance(hashed, str)  # 해싱된 비밀번호는 문자열이어야 함
    assert bcrypt.checkpw(TEST_PASSWORD.encode(), hashed.encode())  # 원본 비밀번호와 비교

# 회원가입 테스트
def test_register_user(db_connection):
    """회원가입 후 DB에 사용자 정보가 저장되는지 확인"""
    success = register_user(TEST_USERNAME, TEST_PASSWORD)
    assert success is True  # 회원가입 성공 여부 확인

    # DB에서 사용자 조회하여 검증
    with db_connection.cursor() as cur:
        cur.execute("SELECT username FROM users WHERE username = %s", (TEST_USERNAME,))
        user = cur.fetchone()
    assert user is not None  # 사용자가 DB에 저장되었는지 확인

# 로그인 테스트 (올바른 비밀번호)
def test_authenticate_success():
    """올바른 비밀번호로 로그인 시 인증이 성공해야 함"""
    assert authenticate(TEST_USERNAME, TEST_PASSWORD) is True

# 로그인 테스트 (잘못된 비밀번호)
def test_authenticate_failure():
    """잘못된 비밀번호로 로그인 시 인증이 실패해야 함"""
    assert authenticate(TEST_USERNAME, "WrongPassword") is False

# 회원 탈퇴 테스트
def test_delete_user(db_connection):
    """회원 탈퇴 후 is_active 상태가 False로 변경되는지 확인"""
    delete_success = delete_user(TEST_USERNAME)
    assert delete_success is True  # 회원 탈퇴 성공 여부 확인

    # DB에서 사용자 is_active 상태 확인
    with db_connection.cursor() as cur:
        cur.execute("SELECT is_active FROM users WHERE username = %s", (TEST_USERNAME,))
        user_status = cur.fetchone()
    assert user_status is not None and user_status[0] is False  # 탈퇴 후 is_active = False 확인
