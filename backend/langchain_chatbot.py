import uuid
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma

# OpenAI 모델 초기화
model = ChatOpenAI()

# RAG를 위한 vector store 연결 및 Embedding 설정
embeddings = OpenAIEmbeddings()
vector_store = Chroma(
    persist_directory="my_vector_store", 
    embedding_function=embeddings
    )
retriever = vector_store.as_retriever()

# 면접 질문 생성
question_prompt = PromptTemplate(
    template="파이썬 면접 질문 하나 생성해.",
    input_variables=[]
)
question_chain = question_prompt | model

# 검색된 문서 가져오기
retrieved_docs = retriever.invoke(generated_question)
context = "\n".join([doc.page_content for doc in retrieved_docs])

# 면접 챗봇 프롬프트 정의
evaluation_prompt = PromptTemplate(
    template="""
    너는 파이썬 면접관 챗봇이야. 
    지원자가 답변을 입력하면 평가하고, 모범답안을 제시해 줘
    
    질문: {question}
    답변: {answer}
    평가:
    """,
    input_variables=["question", "answer"]
)

evaluation_chain = evaluation_prompt | model

# 그래프 정의
workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState):
    response = evaluation_chain.invoke({
        "question": generated_question,
        "answer": state["messages"][-1].content
    })
    return {"messages": [response]}

workflow.add_edge(START, "chain")
workflow.add_node("chain", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# 질문 생성
generated_question = question_chain.invoke({}).content
print(f"Generated Question: {generated_question}")  # 생성된 질문 출력

# 대화 세션 관리
thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}

# 사용자 입력 처리
contents = input("답변 입력: ")
input_message = HumanMessage(content=contents)
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()
