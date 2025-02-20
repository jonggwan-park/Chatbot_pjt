import os
import pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

# 1. Pinecone 초기화
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENV")  # 예: "us-east1-gcp"
pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)

# 2. 사용하려는 인덱스 이름 지정 (이미 생성되어 있어야 함)
index_name = "your-pinecone-index"

# 3. OpenAI 임베딩 함수 설정 (필요한 경우 OpenAI API Key도 함께 지정)
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# 4. 기존의 Pinecone 인덱스를 LangChain 벡터스토어로 래핑
vectorstore = Pinecone.from_existing_index(index_name=index_name, embedding_function=embeddings)

# 5. retriever 생성: 벡터스토어로부터 유사 문서를 검색할 수 있는 retriever 객체 생성
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # top 3 결과 등

# 6. (선택사항) OpenAI LLM과 연결하여 RetrievalQA 체인 생성
llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

# 예시: 질의 실행
query = "Tell me about the tech company Apple."
result = qa_chain.run(query)
print("Answer:", result)
