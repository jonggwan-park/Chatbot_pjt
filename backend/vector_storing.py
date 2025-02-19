from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_openai import OpenAIEmbeddings

# Data Load 데이터 호출 #추가로 필요한 데이터 로더 고려. 
loader = CSVLoader(file_path="data/shopping.csv")
whole_data = loader.load()

# Split 데이터 분할.
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
split_data = splitter.split_documents(whole_data)

# Embedding 임베딩 선언
embeddings = OpenAIEmbeddings()

# Vector Store 데이터 저장. 
vector_store = Chroma.from_documents(
    documents=split_data,
    embedding=embeddings,
    persist_directory="my_vector_store",
)