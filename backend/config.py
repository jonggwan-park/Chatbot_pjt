import streamlit as st
from openai import OpenAI

# Neon PostgreSQL 연결 정보
DB_CONFIG = {
    "host": st.secrets['postgres']['POSTGRES_HOST'],
    "database": st.secrets['postgres']['POSTGRES_DB'],
    "user": st.secrets['postgres']['POSTGRES_USER'],
    "password": st.secrets['postgres']['POSTGRES_PASSWORD'],
    "port": st.secrets['postgres']['POSTGRES_PORT']
}

def get_openai_key():
    return st.secrets['openai']["OPENAI_API_KEY"]

# OpenAI API 클라이언트 설정
def get_openai_client():
    return OpenAI(api_key=st.secrets['openai']["OPENAI_API_KEY"])


# openai 기본 모델 설정
DEFAULT_MODEL = "gpt-3.5-turbo"


SYSTEM_MESSAGE = '''
    너는 IT 기업 면접관임.
    개발자 채용 시 기술 면접을 진행하는 중임. 
    한 번에 하나의 질문을 제시하고, 해당 질문에 답변이 들어오면 
    답변에 대해 피드백을 제공한 후 다음 질문을 시작해.
    '''

# 챗봇 UI 아바타
BOT_AVATAR = 'https://github.com/user-attachments/assets/caedea67-2ccf-459d-b5d8-7a6ffcd8fc24'
USER_AVATAR = 'https://github.com/user-attachments/assets/f77abd1d-5c80-49c2-8225-13e136a6446b'