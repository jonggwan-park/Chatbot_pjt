import streamlit as st
from backend.accounts import authenticate, register_user, login_user, logout


# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None


# 로그인 UI
st.title("🔑 로그인")

if not st.session_state["authenticated"]:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])

    with tab1:
        input_username = st.text_input("아이디", key="input_username")  # 키 충돌 방지
        input_password = st.text_input("비밀번호", type="password", key="input_password")

        if st.button("로그인"):
            if authenticate(input_username, input_password):
                login_user(input_username)  # 세션 상태 업데이트
                st.success(f"🎉 환영합니다, {input_username}님!")
                st.rerun()  # 화면 새로고침하여 UI 반영
            else:
                st.error("❌ 아이디 또는 비밀번호가 잘못되었습니다.")

    with tab2:
        new_username = st.text_input("새 아이디", key="new_username")
        new_password = st.text_input("새 비밀번호", type="password", key="new_password")

        if st.button("회원가입"):
            if register_user(new_username, new_password):
                st.success("✅ 회원가입 성공! 로그인해주세요.")
            else:
                st.error("❌ 이미 존재하는 아이디입니다.")

else:
    st.sidebar.button("로그아웃", on_click=logout)
    st.write(f"✅ 로그인 상태: {st.session_state['user']}님")
