import streamlit as st
from backend.chatbot import initialize_session, display_chat_history, handle_user_input

st.title("AI 면접 도우미 챗봇")

# 챗 초기화 및 UI 표시
initialize_session()
display_chat_history()
handle_user_input()