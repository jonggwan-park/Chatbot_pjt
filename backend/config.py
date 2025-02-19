import streamlit as st

# Neon PostgreSQL 연결 정보
DB_CONFIG = {
    "host": st.secrets['postgres']['POSTGRES_HOST'],
    "database": st.secrets['postgres']['POSTGRES_DB'],
    "user": st.secrets['postgres']['POSTGRES_USER'],
    "password": st.secrets['postgres']['POSTGRES_PASSWORD'],
    "port": st.secrets['postgres']['POSTGRES_PORT']
}