import uuid
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
import streamlit as st
from st_chat_message import message
from backend.config import (get_openai_client,
                            QUESTION_PROMPT,
                            EVALUATION_PROMPT,
                            retriever, 
                            BOT_AVATAR, USER_AVATAR)



# Streamlit 세션 상태 초기화
def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "generated_question" not in st.session_state:
        # RAG를 이용하여 질문 생성을 위한 관련 문서 검색
        retrieved_docs = retriever.invoke("파이썬 면접 질문 하나 생성해")  # 임시 검색 쿼리
        context = "\n".join([doc.page_content for doc in retrieved_docs])  # 검색된 문서에서 내용 가져오기
        
        # 세션 상태에서 context 유지
        st.session_state['context'] = context
        
        # 질문용 모델 체인 정의
        question_chain = QUESTION_PROMPT | get_openai_client()
        
        # RAG와 함께 질문 생성
        st.session_state.generated_question = question_chain.invoke({'context': context}).content



# RAG를 이용하여 피드백을 위해 검색된 문서 가져오기
def feedback_documents():
    if "generated_question" in st.session_state:
        retrieved_docs = retriever.invoke(st.session_state.generated_question)
        st.session_state.feedback_context = "\n".join([doc.page_content for doc in retrieved_docs])


def initialize_evaluation_workflow():
    """ 평가용 모델 체인을 기반으로 LangGraph 워크플로우 초기화 """
    # 그래프 정의
    workflow = StateGraph(state_schema=MessagesState)

    # 모델 평가 함수 정의
    def call_model(state: MessagesState):
        evaluation_chain = EVALUATION_PROMPT | get_openai_client()
        response = evaluation_chain.invoke({
            "question": st.session_state.get("generated_question", ""),
            "answer": state["messages"][-1].content,
            "context": st.session_state.get("context", "")
        })
        return {"messages": [response]}

    # 노드 및 엣지 추가
    workflow.add_node("chain", call_model)
    workflow.add_edge(START, "chain")

    # 체크포인트 메모리 저장
    memory = MemorySaver()
    
    # 워크플로우 컴파일
    app = workflow.compile(checkpointer=memory)
    
    return app


# 채팅 기록 출력 함수
def display_chat_history():
    for i, msg in enumerate(st.session_state.messages):
        is_user = msg["role"] == "user"
        message(msg["content"], is_user=is_user, key=f"msg_{i}", logo=USER_AVATAR if is_user else BOT_AVATAR)



def generate_question():
    """ 사용자의 답변 후 새로운 질문을 생성하는 함수 """
    question_chain = QUESTION_PROMPT | get_openai_client()

    # 새로운 질문 생성
    generated_question = question_chain.invoke(
        {"context": st.session_state.get("context", "")}
    ).content

    # 세션 상태 업데이트
    st.session_state.generated_question = generated_question
    st.session_state.messages.append({"role": "assistant", "content": generated_question})

def handle_user_input():
    """ 사용자 입력을 처리하는 함수 """
    if prompt := st.chat_input("답변을 입력하세요..."):

        # 사용자 입력 저장 및 출력
        st.session_state.messages.append({"role": "user", "content": prompt})
        message(prompt, is_user=True, key=f"user_{len(st.session_state.messages)}", logo=USER_AVATAR)

        # LangGraph 워크플로우를 실행하여 RAG 검색 및 응답 생성
        thread_id = uuid.uuid4()
        config = {"configurable": {"thread_id": thread_id}}

        input_message = {"role": "user", "content": prompt}
        
        # LangGraph 평가 워크플로우 실행
        if "app" not in st.session_state:
            st.session_state.app = initialize_evaluation_workflow()
        
        # AI 평가 수행
        for event in st.session_state.app.stream({"messages": [input_message]}, config, stream_mode="values"):
            response = event["messages"][-1].content

            # ✅ 중복 방지: 동일한 응답이 있는지 확인
            if not any(msg["content"] == response for msg in st.session_state.messages):
                st.session_state.messages.append({"role": "assistant", "content": response})
                message(response, is_user=False, key=f"assistant_{len(st.session_state.messages)}", logo=BOT_AVATAR)

        # ✅ 면접 지속 여부 선택 버튼 추가
        st.session_state.show_continue_button = True
