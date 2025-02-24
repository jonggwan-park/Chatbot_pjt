from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


class PineconeWrapper:
    def __init__(
        self,
        api_key,
        index_name,
        environment,
        dimension=384,
        metric="cosine",
        namespace="example-namespace",
    ):
        """
        초기화 및 인덱스 생성
        :param api_key: Pinecone API 키
        :param index_name: 사용할 인덱스 이름
        :param environment: Pinecone 환경 (예: "us-east1-gcp")
        :param dimension: 벡터 차원 수 (임베딩 모델에 따라 달라짐)
        :param metric: 유사도 측정 방식 (예: "cosine")
        :param namespace: 데이터를 저장할 네임스페이스 이름
        """
        self.api_key = api_key
        self.index_name = index_name
        self.environment = environment
        self.dimension = dimension
        self.metric = metric
        self.namespace = namespace

        # Pinecone 클라이언트 생성
        self.pc = Pinecone(api_key=self.api_key)

        # 인덱스 존재 여부 확인 (pinecone.list_indexes()는 구버전에서는 list 반환)
        existing_indexes = self.pc.list_indexes()  # list 형태
        if self.index_name not in existing_indexes:
            print(f"인덱스 '{self.index_name}'가 없으므로 생성합니다.")
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
            except Exception as e:
                if "ALREADY_EXISTS" in str(e):
                    print(
                        f"인덱스 '{self.index_name}'가 이미 존재합니다. 계속 진행합니다."
                    )
                else:
                    raise e
        else:
            print(f"인덱스 '{self.index_name}'가 이미 존재합니다.")

        # 인덱스 객체 가져오기
        self.index = self.pc.Index(self.index_name)

    def upsert_data(self, data, model="multilingual-e5-large"):
        """
        주어진 데이터를 임베딩 후 업서트
        :param data: [{"id": ..., "text": ...}, ...] 형태의 데이터 리스트
        :param model: 사용 할 임베딩 모델 이름
        """
        # 임베딩 수행: data의 "text" 항목들을 embed
        texts = [item["text"] for item in data]
        embeddings = self.pc.inference.embed(
            model=model,
            inputs=texts,
            parameters={"input_type": "passage", "truncate": "END"},
        )
        records = []
        for item, emb in zip(data, embeddings):
            records.append(
                {
                    "id": item["id"],
                    "values": emb["values"],
                    "metadata": {"text": item["text"]},
                }
            )
        # 업서트 수행 (namespace 사용)
        self.index.upsert(vectors=records, namespace=self.namespace)
        print("✅ 데이터 업서트 완료.")

    def query(self, query_text, model="multilingual-e5-large", top_k=3):
        """
        쿼리 텍스트를 임베딩하여 인덱스에서 유사한 벡터 검색
        :param query_text: 검색할 문장
        :param model: 사용 할 임베딩 모델 이름 (query 용)
        :param top_k: 반환할 상위 유사 벡터 수
        :return: 검색 결과 (dict)
        """
        query_embedding = self.pc.inference.embed(
            model=model, inputs=[query_text], parameters={"input_type": "query"}
        )
        results = self.index.query(
            namespace=self.namespace,
            vector=query_embedding[0].values,
            top_k=top_k,
            include_values=False,
            include_metadata=True,
        )
        return results


# main.py에서 실행할 것

# import os
# from dotenv import load_dotenv
# from backend.pinecone_db import PineconeWrapper
# from pinecone import Pinecone

# # .env 파일 로드
# load_dotenv()
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_ENV = os.getenv("PINECONE_ENV")

# # PineconeWrapper 인스턴스 생성
# index_name = "example-index"  # 원하는 인덱스 이름

# pinecone_client = PineconeWrapper(
#     api_key=PINECONE_API_KEY,
#     index_name=index_name,
#     environment=PINECONE_ENV,
#     dimension=384,  # 사용하려는 임베딩 모델의 차원 (예: all-MiniLM-L6-v2 → 384)
#     metric="cosine",
#     namespace="example-namespace" # 인덱스 내 저장소 이름
# )

# # 예시 데이터 (여기서는 면접 질문, 일반 텍스트 예시로 사용)
# data = [
#     {"id": "vec1", "text": "Apple is a popular fruit known for its sweetness and crisp texture."},
#     {"id": "vec2", "text": "The tech company Apple is known for its innovative products like the iPhone."},
#     {"id": "vec3", "text": "Many people enjoy eating apples as a healthy snack."},
#     {"id": "vec4", "text": "Apple Inc. has revolutionized the tech industry with its sleek designs and user-friendly interfaces."},
#     {"id": "vec5", "text": "An apple a day keeps the doctor away, as the saying goes."},
#     {"id": "vec6", "text": "Apple Computer Company was founded on April 1, 1976, by Steve Jobs, Steve Wozniak, and Ronald Wayne as a partnership."}
# ]

# # 데이터 업서트 실행
# pinecone_client.upsert_data(data)

# # 쿼리 실행
# query = "Tell me about the tech company known as Apple."
# results = pinecone_client.query(query)
# print("검색 결과:")
# print(results)
