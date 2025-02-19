import streamlit as st
from st_chat_message import message
from backend.config import (get_openai_client, 
                            DEFAULT_MODEL, 
                            SYSTEM_MESSAGE,
                            BOT_AVATAR, USER_AVATAR)

# OpenAI API 클라이언트 초기화
def initialize_session():
    """세션 상태를 초기화"""
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = DEFAULT_MODEL

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_MESSAGE}]


def display_chat_history():
    """채팅 기록을 화면에 출력하는 함수"""
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "system":  # 시스템 메시지는 출력하지 않음
            continue
        is_user = msg["role"] == "user"
        message(msg["content"], is_user=is_user, key=f"msg_{i}")


def get_openai_response(messages):
    """OpenAI API를 호출하여 응답을 가져옴"""
    response = get_openai_client().chat.completions.create(
        model=st.session_state["openai_model"],
        messages=messages,
        stream=False,
    )
    return response.choices[0].message.content


def handle_user_input():
    """사용자의 입력을 처리하고 OpenAI API 응답을 가져옴"""
    if prompt := st.chat_input("질문을 입력하세요..."):
        # 사용자 입력을 대화 기록에 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        message(prompt, is_user=True, key=f"user_{len(st.session_state.messages)}", logo=f'{USER_AVATAR}')

        # OpenAI API 응답 가져오기
        response = get_openai_response(st.session_state.messages)

        # OpenAI 응답을 대화 기록에 추가
        st.session_state.messages.append({"role": "assistant", "content": response})
        message(response, is_user=False, key=f"assistant_{len(st.session_state.messages)}", logo=f'{BOT_AVATAR}')