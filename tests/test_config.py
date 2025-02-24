from dotenv import load_dotenv
from backend.config import (
    DB_CONFIG,
    PINECONE_CONFIG,
    DEFAULT_MODEL,
    get_openai_client,
    get_openai_key,
)

# .env 파일 로드
load_dotenv()


def test_db_config():
    """PostgreSQL 데이터베이스 환경변수 설정 테스트"""
    required_keys = ["host", "database", "user", "password", "port"]
    for key in required_keys:
        assert key in DB_CONFIG
        assert DB_CONFIG[key] is not None  # 값이 설정되어 있어야 함


def test_pinecone_config():
    """Pinecone 설정 환경변수 테스트"""
    required_keys = ["api_key", "environment", "index_name"]
    for key in required_keys:
        assert key in PINECONE_CONFIG
        assert PINECONE_CONFIG[key] is not None  # 값이 설정되어 있어야 함


def test_defaults():
    """기본 설정값 테스트"""
    assert DEFAULT_MODEL == "gpt-4o-mini"  # 기본 모델이 정확하게 설정되었는지 확인


def test_openai_key():
    """OpenAI API 키가 설정되어 있는지 확인"""
    api_key = get_openai_key()
    assert api_key is not None
    assert isinstance(api_key, str)
    assert len(api_key) > 0  # API 키는 빈 문자열이 아니어야 함


def test_openai_client():
    """OpenAI 클라이언트 생성 테스트"""
    client = get_openai_client()
    assert client is not None
