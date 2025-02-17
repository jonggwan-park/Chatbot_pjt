import streamlit as st
from openai import OpenAI

st.title("ChatGPT-like clone") # 제목 출력. 

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) #api 키 제공

# Set a default model 기본 모델 설정
if "openai_model" not in st.session_state: #session_state에 openai_model값이 없으면
    st.session_state["openai_model"] = "gpt-3.5-turbo" #모델 지정

sys_message = '''
너는 it기업 면접관임
개발자 채용시 기술 면접을 진행하는 중임. 
한번에 하나의 질문을 제시하고, 해당 질문에 답변이 들어오면 해당 답변에 대해 피드백을 진행 한 후 다음 질문을 시작해. 
        
'''

# Initialize chat history
if "messages" not in st.session_state: #session_state에 message가 없으면
    st.session_state.messages = [] #초기화
    st.session_state.messages = [{"role": "system", "content": sys_message}]


# Display chat messages from history on app rerun
for message in st.session_state.messages: #message가 있으면 
    if message["role"] == "system":  # 시스템 메시지는 출력하지 않음
        continue  
    with st.chat_message(message["role"]):# role 에 따라 출력. 
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"): #프롬프트에 st.chat_input에서 입력한 값 대입
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt}) #message탭에 user /content에 추가. 
    # Display user message in chat message container
    with st.chat_message("user"): #user 출력. 
        st.markdown(prompt)
# Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],#openai_model로 
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream) #출력 생성. 
    st.session_state.messages.append({"role": "assistant", "content": response})
