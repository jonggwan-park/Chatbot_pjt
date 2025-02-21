import streamlit as st
from backend.langchain_chatbot import (
    initialize_session,
    display_chat_history,
    handle_user_input,
    feedback_documents,
    initialize_evaluation_workflow,
    generate_question
)

# Streamlit UI 실행 함수
st.set_page_config(page_title="AI 면접 도우미 챗봇")
st.title("AI 면접 도우미 챗봇")

# 세션 상태 초기화
initialize_session()

# 피드백 문서 검색
feedback_documents()

# LangGraph 평가 워크플로우 초기화 (세션에 저장)
if "app" not in st.session_state:
    st.session_state.app = initialize_evaluation_workflow()

# 채팅 기록 출력
display_chat_history()

# 면접 시작 버튼
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if not st.session_state.interview_started:
    if st.button("면접 시작하기"):
        st.session_state.interview_started = True
        st.session_state.show_continue_button = False  # 새 질문 생성 시 버튼 숨김
        generate_question()  # 첫 질문 생성

# 사용자 입력 받기
handle_user_input()

# 면접 지속 여부 버튼 표시
if st.session_state.get("show_continue_button", False):
    st.write("면접을 계속하시겠습니까?")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("계속 진행"):
            st.session_state.show_continue_button = False  # 버튼 숨기기
            generate_question()  # 다음 질문 생성

    with col2:
        if st.button("종료하고 저장"):
            st.write("면접을 종료합니다.")
            st.session_state.interview_started = False
            st.session_state.show_continue_button = False  # 버튼 숨김
            st.session_state.chat_history = []  # 채팅 기록 초기화
            st.rerun()  # 페이지 새로고침