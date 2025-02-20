from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader, Docx2txtLoader
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


# Data Load 데이터 호출
loader = Docx2txtLoader(file_path="data/referance.docx")
whole_data = loader.load()
# print(whole_data)

# Split 데이터 분할.
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
split_data = splitter.split_documents(whole_data)
print(split_data[0])

# Embedding 임베딩
embeddings = OpenAIEmbeddings()

# Vector Store 데이터 저장. 
vector_store = Chroma.from_documents(
    documents=split_data,
    embedding=embeddings,
    persist_directory="my_vector_store",
)
