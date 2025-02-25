# AI 기반 대화형 챗봇 프로젝트 💬


## 1. 프로젝트 개요
AI 기반 **대화형 챗봇**을 개발하는 프로젝트입니다.
LangChain과 Pinecone을 활용한 **RAG(Retrieval-Augmented Generation)** 모델을 기반으로,
주어진 문서를 참고하여 **면접 질문을 생성하고 답변을 평가**하는 기능을 제공합니다.

## 사용 기술
- **백엔드:** Python, Streamlit
- **LLM:** OpenAI GPT-4o Mini
- **벡터 데이터베이스:** Pinecone
- **DB:** PostgreSQL (Neon)
- **인프라:** Streamlit Cloud (배포), GitHub Actions (CI)
- **테스트:** Pytest

---

## 2. 배포
👉 **[배포 URL](https://chatbotpjt-udbkrmgy8v64nxax3baeae.streamlit.app/)**

---

## 3. 팀원 구성

- 팀장 : 신제창
- 팀원 : 이현지, 박종관, 박민지

### - 역할 분담
- Chatbot 모델 - 신제창
- 웹-Streamlit - 이현지
- RDB, 벡터DB - 박민지, 박종관

---

## 3. 주요 기능
### - 면접 질문 생성
- Pinecone에 저장된 문서를 바탕으로 GPT-4o Mini가 적절한 면접 질문을 생성

### - 답변 평가
- 사용자가 입력한 답변을 LangChain RAG 기반으로 평가
- 참고 문서와 비교하여 **피드백 및 모범 답안 제공**

### - 채팅 내역 저장
- 사용자별 채팅 세션을 생성하고 데이터베이스에 저장
- PostgreSQL을 활용하여 채팅 내역 조회 가능

---

## 3. 프로젝트 구조

```bash
📦 Chatbot_pjt/            # 프로젝트 루트 폴더
│
│── main.py                # 앱의 진입점 (메인 페이지)
│
│── 📂 pages/              # 여러 개의 페이지를 관리하는 폴더
│   │── home.py            # 기본 정보를 제공, 앱의 목적 안내 ex) 사용법
│   │── chat.py            # 챗봇 페이지
│   └── history.py         # 대화 기록 조회 페이지
│
│── 📂 data/               # 챗봇의 데이터셋
│   └── referance.docx     # 데이터셋
│
│── 📂 backend/            # 백엔드 로직 (DB, API 등)
│   │── db.py              # DB 연결 및 관리
│   │── accounts.py        # 사용자 관리 및 인증 (회원가입, 로그인)
│   │── config.py          # 프로젝트 설정 파일 (환경 변수 및 설정값 로드)
│   │── langchain_chatbot.py # LangChain을 활용한 LLM 기반 챗봇 구현 (RAG 포함)
│   │── pinecone_db.py     # Pinecone 데이터베이스 관리
│   └── utils.py           # 유틸리티 함수
│
│── 📂 tests/              # 테스트 코드 폴더 (pytest 활용)
│   │── init.py             # 테스트 패키지로 인식되도록 하는 초기화 파일
│   │── test_accounts.py    # 회원가입 및 로그인 기능 테스트
│   │── test_db.py          # 데이터베이스 관련 기능 테스트
│   │── langchain_chatbot.py # 챗봇 기능 테스트
│   └── test_pinecone_db.py # Pinecone 벡터 데이터베이스 기능 테스트
│
│── 📂 .streamlit/         # Streamlit 설정 파일
│   └── secrets.toml       # 환경 변수 (DB, API Key)
│
│── requirements.txt       # 설치할 라이브러리 목록
│── venv                   # 가상환경
│── .env                   # 환경변수 관리 파일
│── .gitignore             # Git 관리 파일
└── README.md              # 프로젝트 설명
```

---

## 4. 환경 변수 설정

### - 스트림릿 클라우드 배포 환경 변수

스트림릿 클라우드에서는 `.streamlit/secrets.toml`을 사용해 환경 변수를 설정합니다.

**예제 (`.streamlit/secrets.toml`)**

```toml
[openai]
OPENAI_API_KEY = "your-openai-api-key"

[postgres]
POSTGRES_HOST = "your-db-host"
POSTGRES_DB = "your-db-name"
POSTGRES_USER = "your-db-user"
POSTGRES_PASSWORD = "your-db-password"
POSTGRES_PORT = "5432"

[pinecone]
PINECONE_API_KEY = "your-pinecone-api-key"
PINECONE_ENV = "your-pinecone-env"
PINECONE_INDEX_NAME = "your-index-name"

```

**⚠️ 중요:**

스트림릿 클라우드에 배포할 경우, `secrets.toml`에 저장한 환경 변수는 `st.secrets`를 사용해 불러옵니다.


### - 로컬 테스트 환경 변수

테스트(`tests/` 폴더)에서는 **`.env` 파일을 사용하여 환경 변수를 설정**합니다.

**예제 (`.env`)**

```
OPENAI_API_KEY=your-openai-api-key
POSTGRES_HOST=your-db-host
POSTGRES_DB=your-db-name
POSTGRES_USER=your-db-user
POSTGRES_PASSWORD=your-db-password
POSTGRES_PORT=5432
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENV=your-pinecone-env
PINECONE_INDEX_NAME=your-index-name

```

테스트 실행 시 `.env`를 로드하려면 **`python-dotenv`** 패키지를 설치하고 `load_dotenv()`를 사용해야 합니다.

---

## ▶️ 로컬 실행 방법

1. **Python 가상환경 설정 (권장)**

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate      # Windows
```

1. **필요한 패키지 설치**

```bash
pip install -r requirements.txt
```

1. **환경 변수 설정**
    - `.streamlit/secrets.toml` 파일을 생성하고 OpenAI, DB, Pinecone 키를 입력합니다.
    - `.env` 파일을 생성하여 테스트 환경 변수를 설정합니다.
2. **Streamlit 앱 실행**

```bash
streamlit run main.py
```

---

## ▶️ 테스트 실행 방법

테스트는 `pytest`를 사용하여 실행합니다.

```bash
pytest tests/
```

CI/CD에서는 GitHub Actions를 통해 자동으로 실행됩니다.

---

## 5. GitHub Actions CI 설정

본 프로젝트는 **GitHub Actions**를 사용하여 CI를 자동화합니다.

테스트 및 코드 스타일 검사를 실행하는 **CI 워크플로우 (`.github/workflows/ci.yml`)** 포함.

---

## 6. 참고 사항

- 스트림릿 클라우드에서 배포된 프로젝트는 GitHub의 `main` 브랜치 업데이트 시 자동 반영됩니다.

