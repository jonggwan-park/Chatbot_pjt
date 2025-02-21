import uuid
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
import streamlit as st
from backend.config import (get_openai_key, 
                            DEFAULT_MODEL, 
                            BOT_AVATAR, USER_AVATAR)

#streamlit api 키 호출
key = get_openai_key()

# OpenAI 모델 초기화
model = ChatOpenAI(model=DEFAULT_MODEL, temperature=0.7, api_key= key)

# RAG를 위한 vector store 연결 및 Embedding 설정
embeddings = OpenAIEmbeddings()
vector_store = Chroma(
    persist_directory="my_vector_store", 
    embedding_function=embeddings
    )
retriever = vector_store.as_retriever()

# # 토픽 선택용 코드 추후 필요시 사용. 
# # 면접 질문 생성
# question_prompt = PromptTemplate(
#     template="""주어진 문서를 기반으로 {topic} 면접 질문을 생성해 주세요. 
#     문서 내용: {context}
#     면접 질문:""",
#     input_variables=["context", "topic"]  # "context"와 "topic"을 입력 변수로 추가
# )

# # 사용자가 원하는 주제 입력
# topic = input("면접 질문을 생성할 주제를 입력하세요 (예: 파이썬): ")

# # RAG를 이용하여 관련 문서 검색
# retrieved_docs = retriever.invoke(topic)  # 사용자가 입력한 주제를 검색 쿼리로 사용
# context = "\n".join([doc.page_content for doc in retrieved_docs])  # 검색된 문서에서 내용 가져오기

# # RAG와 함께 질문 생성
# question_chain = question_prompt | model
# generated_question = question_chain.invoke({"context": context, "topic": topic}).content

# print(f"Generated Question: {generated_question}")  # 생성된 질문 출력


# 면접 질문 생성
question_prompt = PromptTemplate(
    template="""주어진 문서를 기반으로 파이썬 면접 질문을 하나만 생성해 주세요. 
    문서 내용: {context}
    면접 질문:""",
    input_variables=["context"]  # "context"를 입력 변수로 추가
)

# 면접 챗봇 프롬프트 정의
evaluation_prompt = PromptTemplate(
    template="""
    너는 파이썬 면접관 챗봇이야. 
    지원자가 답변을 입력하면 아래의 문서를 참조해서 평가 및 모범답안을 제시를 수행해줘
    
    참고 문서:  
    {context}
    
    질문: {question}
    답변: {answer}
    평가:
    
    """,
    input_variables=["question", "answer"]
)

# RAG를 이용하여 질문 생성을 위한 관련 문서 검색
retrieved_docs = retriever.invoke("파이썬 면접 질문 하나 생성해")  # 임시로 사용한 검색 쿼리
context = "\n".join([doc.page_content for doc in retrieved_docs])  # 검색된 문서에서 내용 가져오기

#질문용 모델 체인 정의
question_chain = question_prompt | model

# RAG와 함께 질문 생성
generated_question = question_chain.invoke({"context": context}).content

# RAG를 이용하여 피드백을 위해 검색된 문서 가져오기
retrieved_docs = retriever.invoke(generated_question)
context = "\n".join([doc.page_content for doc in retrieved_docs])

#평가용 모델 체인 정의 
evaluation_chain = evaluation_prompt | model


# 그래프 정의
workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState):
    response = evaluation_chain.invoke({
        "question": generated_question,
        "answer": state["messages"][-1].content,
        "context": context
    })
    return {"messages": [response]}

workflow.add_edge(START, "chain")
workflow.add_node("chain", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


while True :
    # 질문 생성
    generated_question = question_chain.invoke({}).content
    print(f"Generated Question: {generated_question}")  # 생성된 질문 출력
    # 대화 세션 관리
    thread_id = uuid.uuid4()
    config = {"configurable": {"thread_id": thread_id}}
    # 사용자 입력 처리
    contents = input("답변 입력: ")
    if contents == "exit":
        sys.exit()
    input_message = HumanMessage(content=contents)
    for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
        event["messages"][-1].pretty_print()
    print("")








# # 토픽 선택용 코드 추후 필요시 사용. 
# # 면접 질문 생성
# question_prompt = PromptTemplate(
#     template="""주어진 문서를 기반으로 {topic} 면접 질문을 생성해 주세요. 
#     문서 내용: {context}
#     면접 질문:""",
#     input_variables=["context", "topic"]  # "context"와 "topic"을 입력 변수로 추가
# )

# # 사용자가 원하는 주제 입력
# topic = input("면접 질문을 생성할 주제를 입력하세요 (예: 파이썬): ")

# # RAG를 이용하여 관련 문서 검색
# retrieved_docs = retriever.invoke(topic)  # 사용자가 입력한 주제를 검색 쿼리로 사용
# context = "\n".join([doc.page_content for doc in retrieved_docs])  # 검색된 문서에서 내용 가져오기

# # RAG와 함께 질문 생성
# question_chain = question_prompt | model
# generated_question = question_chain.invoke({"context": context, "topic": topic}).content

# print(f"Generated Question: {generated_question}")  # 생성된 질문 출력