import streamlit as st
from openai import OpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate

# Neon PostgreSQL 연결 정보
DB_CONFIG = {
    "host": st.secrets['postgres']['POSTGRES_HOST'],
    "database": st.secrets['postgres']['POSTGRES_DB'],
    "user": st.secrets['postgres']['POSTGRES_USER'],
    "password": st.secrets['postgres']['POSTGRES_PASSWORD'],
    "port": st.secrets['postgres']['POSTGRES_PORT']
}


# openai 기본 모델 설정
DEFAULT_MODEL = "gpt-4o-mini"

# OpenAI API 클라이언트 설정
def get_openai_client():
    return ChatOpenAI(model= DEFAULT_MODEL, temperature=0.7, api_key=st.secrets['openai']["OPENAI_API_KEY"])


# 면접 질문 생성 프롬프트
QUESTION_PROMPT = PromptTemplate(
    template="""주어진 문서를 기반으로 파이썬 면접 질문을 하나만 생성해 주세요. 
    문서 내용: {context}
    면접 질문:""",
    input_variables=["context"]
)

# 면접 챗봇 평가 프롬프트
EVALUATION_PROMPT = PromptTemplate(
    template="""
    너는 파이썬 면접관 챗봇이야. 
    지원자가 답변을 입력하면 아래의 문서를 참조해서 평가 및 모범답안을 제시해줘
    
    참고 문서:  
    {context}
    
    질문: {question}
    답변: {answer}
    평가:
    """,
    input_variables=["question", "answer", "context"]
)

# RAG 설정
VECTOR_STORE_PATH = "my_vector_store"

# Embedding 설정
embeddings = OpenAIEmbeddings(api_key=st.secrets['openai']["OPENAI_API_KEY"])
vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
retriever = vector_store.as_retriever()


# 챗봇 UI 아바타
BOT_AVATAR = 'https://github.com/user-attachments/assets/caedea67-2ccf-459d-b5d8-7a6ffcd8fc24'
USER_AVATAR = 'https://github.com/user-attachments/assets/f77abd1d-5c80-49c2-8225-13e136a6446b'