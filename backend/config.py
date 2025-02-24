import streamlit as st
from openai import OpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
# from pinecone import Pinecone, ServerlessSpec
import pinecone
from langchain_pinecone import PineconeVectorStore
# Neon PostgreSQL 연결 정보
DB_CONFIG = {
    "host": st.secrets['postgres']['POSTGRES_HOST'],
    "database": st.secrets['postgres']['POSTGRES_DB'],
    "user": st.secrets['postgres']['POSTGRES_USER'],
    "password": st.secrets['postgres']['POSTGRES_PASSWORD'],
    "port": st.secrets['postgres']['POSTGRES_PORT']
}

PINECONE_CONFIG = {
    "api_key": st.secrets['pinecone']['PINECONE_API_KEY'],
    "environment": st.secrets['pinecone']['PINECONE_ENV'],
    "index_name": st.secrets['pinecone']['PINECONE_INDEX_NAME']
}

# openai 기본 모델 설정
DEFAULT_MODEL = "gpt-4o-mini"

# OpenAI API 클라이언트 설정
def get_openai_client():
    return ChatOpenAI(model= DEFAULT_MODEL, temperature=0.9, api_key=st.secrets['openai']["OPENAI_API_KEY"],max_completion_tokens=1500)

def get_openai_key():
    return st.secrets['openai']["OPENAI_API_KEY"]

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

embeddings = OpenAIEmbeddings(api_key=get_openai_key())

PINECONE_API_KEY = PINECONE_CONFIG["api_key"]
PINECONE_ENV = PINECONE_CONFIG["environment"]
INDEX_NAME = PINECONE_CONFIG["index_name"]

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# # Now do stuff
# if index_name not in pc.list_indexes().names():
#     pc.create_index(
#         name=index_name,
#         dimension=1536,
#         metric='cosine',
#         spec=ServerlessSpec(
#             cloud='aws',
#             region='us-east-1'
#         )
#     )

# index 객체 생성
if INDEX_NAME not in pc.list_indexes().names():
    raise ValueError(f"Pinecone 인덱스 '{INDEX_NAME}'가 존재하지 않습니다. 먼저 생성해 주세요.")

index = pc.Index(INDEX_NAME)

# Vector Store 생성 (LangChain용)
vectorstore = PineconeVectorStore(index, embeddings,namespace="example-namespace")
print(type(vectorstore))  # <class 'langchain_pinecone.vectorstores.Pinecone'>

# retriever로 변환
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

QUERY="파이썬 면접 질문 하나 생성해"

# 챗봇 UI 아바타
BOT_AVATAR = 'https://github.com/user-attachments/assets/caedea67-2ccf-459d-b5d8-7a6ffcd8fc24'
USER_AVATAR = 'https://github.com/user-attachments/assets/f77abd1d-5c80-49c2-8225-13e136a6446b'

# # RAG 설정
# VECTOR_STORE_PATH = "my_vector_store"

# # Embedding 설정
# embeddings = OpenAIEmbeddings()
# vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
# retriever = vector_store.as_retriever()


