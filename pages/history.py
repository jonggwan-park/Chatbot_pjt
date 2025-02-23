import streamlit as st
from backend.db import get_user_chat_sessions, get_chat_history, get_user_id
from backend.accounts import is_authenticated

# 채팅 히스토리 조회 페이지
def display_chat_history():
    """사용자의 모든 채팅 세션과 선택한 세션의 대화 내역을 조회하는 UI"""
    
    # 로그인 여부 확인
    if not is_authenticated():
        st.warning("로그인이 필요합니다.")
        return
    
    username = st.session_state["user"]  # 현재 로그인한 사용자 이름
    
    # 사용자 ID 가져오기
    user_id = get_user_id(username)
    if not user_id:
        st.error("사용자 정보를 찾을 수 없습니다.")
        return

    # 사용자의 채팅 세션 목록 가져오기
    sessions = get_user_chat_sessions(user_id)
    
    if not sessions:
        st.info("저장된 채팅 내역이 없습니다.")
        return

    # 사용자가 확인할 채팅 세션 선택
    session_options = {session["id"]: session["created_at"] for session in sessions}
    selected_session_id = st.selectbox("조회할 채팅 세션을 선택하세요", options=session_options.keys(), format_func=lambda x: session_options[x])

    # 특정 세션의 대화 내역 가져오기
    chat_history = get_chat_history(selected_session_id)
    
    if not chat_history:
        st.info("이 세션에는 대화 기록이 없습니다.")
        return
    
    # 채팅 내역 표시
    st.subheader(f"채팅 내역 (세션 ID: {selected_session_id})")
    
    for chat in chat_history:
        sender = "🧑‍💻 사용자" if chat["sender"] == "user" else "🤖 챗봇"
        st.markdown(f"**{sender} ({chat['timestamp']}):**")
        st.write(chat["message"])
        st.markdown("---")

# Streamlit 실행 시 메인 함수 호출
if __name__ == "__main__":
    st.title("📜 채팅 히스토리")
    display_chat_history()
