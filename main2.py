import os
from dotenv import load_dotenv
from backend.pinecone_db import PineconeWrapper
from pinecone import Pinecone

# .env 파일 로드
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")

# PineconeWrapper 인스턴스 생성
index_name = "example-index"  # 원하는 인덱스 이름

pinecone_client = PineconeWrapper(
    api_key=PINECONE_API_KEY,
    index_name=index_name,
    environment=PINECONE_ENV,
    dimension=384,  # 사용하려는 임베딩 모델의 차원 (예: all-MiniLM-L6-v2 → 384)
    metric="cosine", 
    namespace="example-namespace" # 인덱스 내 저장소 이름
)

# 예시 데이터 (여기서는 면접 질문, 일반 텍스트 예시로 사용)
data = [
    {"id": "vec1", "text": "Apple is a popular fruit known for its sweetness and crisp texture."},
    {"id": "vec2", "text": "The tech company Apple is known for its innovative products like the iPhone."},
    {"id": "vec3", "text": "Many people enjoy eating apples as a healthy snack."},
    {"id": "vec4", "text": "Apple Inc. has revolutionized the tech industry with its sleek designs and user-friendly interfaces."},
    {"id": "vec5", "text": "An apple a day keeps the doctor away, as the saying goes."},
    {"id": "vec6", "text": "Apple Computer Company was founded on April 1, 1976, by Steve Jobs, Steve Wozniak, and Ronald Wayne as a partnership."}
]

# 데이터 업서트 실행
pinecone_client.upsert_data(data)

# 쿼리 실행
query = "Tell me about the tech company known as Apple."
results = pinecone_client.query(query)
print("검색 결과:")
print(results)



# 프롬프트에 집어넣는법


# PineconeWrapper의 query 메서드를 통해 결과를 받아옵니다.
results = pinecone_client.query(query)

# 결과의 matches 리스트에서 각 항목의 metadata에 저장된 텍스트를 추출합니다.
# (예시에서는 metadata에 'text'라는 키로 저장되어 있다고 가정합니다.)
context_texts = [match["metadata"]["text"] for match in results["matches"]]

# 여러 개의 텍스트를 하나의 문자열로 결합 (필요에 따라 구분자나 정제 로직 추가)
context = "\n".join(context_texts)

# LLM 프롬프트 생성 예시:
prompt = f"""
당신은 신입 AI개발자 면접관입니다.
다음의 질문들을 참고하여 질문을 생성해주세요.

문맥:
{context}

질문:
{query}
"""

print("LLM 프롬프트:")
print(prompt)