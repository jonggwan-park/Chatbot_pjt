import pytest
import streamlit as st
from backend.accounts import (
    register_user,
    authenticate,
    delete_user,
    login_user,
    logout,
    is_authenticated,
)
from backend.db import get_connection, release_connection

# 테스트용 계정 정보
TEST_USERNAME = "pytest_test_user"
TEST_PASSWORD = "TestPassword123!"


@pytest.fixture(scope="module")
def db_connection():
    """데이터베이스 연결을 설정하고 테스트 후 정리"""
    conn = get_connection()
    yield conn
    release_connection(conn)


@pytest.fixture(autouse=True)
def cleanup_user(db_connection):
    """테스트 전후로 DB에서 테스트 사용자 데이터를 정리"""
    with db_connection.cursor() as cur:
        cur.execute("DELETE FROM users WHERE username = %s;", (TEST_USERNAME,))
        db_connection.commit()
    yield
    with db_connection.cursor() as cur:
        cur.execute("DELETE FROM users WHERE username = %s;", (TEST_USERNAME,))
        db_connection.commit()


@pytest.fixture(autouse=True)
def reset_streamlit_session():
    """각 테스트 전 Streamlit 세션 초기화"""
    st.session_state.clear()
    yield
    st.session_state.clear()


def test_register_user():
    """사용자 등록 테스트"""
    result = register_user(TEST_USERNAME, TEST_PASSWORD)
    assert result is True  # 성공적으로 등록되어야 함


def test_authenticate():
    """사용자 인증 테스트"""
    register_user(TEST_USERNAME, TEST_PASSWORD)
    assert authenticate(TEST_USERNAME, TEST_PASSWORD) is True  # 올바른 비밀번호
    assert authenticate(TEST_USERNAME, "wrongpassword") is False  # 잘못된 비밀번호


def test_register_duplicate():
    """중복 사용자 등록 방지 확인"""
    register_user(TEST_USERNAME, TEST_PASSWORD)
    result = register_user(TEST_USERNAME, TEST_PASSWORD)
    assert result is False  # 같은 사용자 등록 시 False 반환


def test_delete_user():
    """회원 탈퇴 후 로그인 불가 확인"""
    register_user(TEST_USERNAME, TEST_PASSWORD)
    assert delete_user(TEST_USERNAME) is True  # 탈퇴 성공
    assert (
        authenticate(TEST_USERNAME, TEST_PASSWORD) is False
    )  # 탈퇴한 계정은 로그인 불가


def test_login_logout():
    """Streamlit 세션을 활용한 로그인/로그아웃 테스트"""
    register_user(TEST_USERNAME, TEST_PASSWORD)

    login_user(TEST_USERNAME)
    assert st.session_state["authenticated"] is True
    assert st.session_state["user"] == TEST_USERNAME

    logout()
    assert st.session_state["authenticated"] is False
    assert st.session_state["user"] is None


def test_is_authenticated():
    """is_authenticated 함수의 동작 확인"""
    assert is_authenticated() is False  # 초기 상태
    login_user(TEST_USERNAME)
    assert is_authenticated() is True  # 로그인 후 True 반환
    logout()
    assert is_authenticated() is False  # 로그아웃 후 False 반환
