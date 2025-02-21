'''
날짜 및 시간 관련 함수
- 대화 기록을 저장할 때 타임스탬프를 추가하는 데 유용

텍스트 전처리 함수
- 사용자가 입력한 텍스트를 정리하거나, 검색 기능을 최적화할 때 유용

데이터베이스 관련 보조 함수
- DB에서 불러온 데이터를 예쁘게 포맷팅할 때 사용

로깅(Logging) 함수
- 에러 발생 시 원인을 쉽게 추적할 수 있도록 로그를 남길 때 유용
'''

import streamlit as st
from backend.accounts import logout

def show_sidebar():
    """로그인 상태일 때 모든 페이지에 로그아웃 버튼 표시"""
    if st.session_state.get("authenticated", False):
        with st.sidebar:
            st.write(f"✅ 로그인 상태: {st.session_state['user']}님")
            if st.button("로그아웃"):
                logout()
                st.success('로그아웃 되었습니다.')
                st.rerun()