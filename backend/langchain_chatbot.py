import uuid
from langchain_openai import ChatOpenAI
from IPython.display import Image, display
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import PromptTemplate

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

template = """
{subject}의 수도에 대해서 알려주세요.
도시의 특징을 다음의 양식에 맞게 불렛 포인트 형식으로 정리해 주세요.
300자 내외로 작성해 주세요.
한글로 작성해 주세요.
----
[양식]
1. 면적
2. 인구
3. 역사적 장소
4. 특산품

#Answer:
"""
prompt = PromptTemplate(
    template=template,    
    input_variables=["subject"]
)

# Define a chat model
model = ChatOpenAI()
chain = prompt | model
# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    # We return a list, because this will get added to the existing list
    return {"messages": response}


# Define the two nodes we will cycle between
workflow.add_edge(START, "chain") #시작에 model을 연결. 
workflow.add_node("chain", call_model)

# Adding memory is straight forward in langgraph!
memory = MemorySaver()

app = workflow.compile(
    checkpointer=memory
)


# The thread id is a unique key that identifies
# this particular conversation.
# We'll just generate a random uuid here.
# This enables a single application to manage conversations among multiple users.
thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}

#입력 처리 기능.
contents = input()
input_message = HumanMessage(content=contents)
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()