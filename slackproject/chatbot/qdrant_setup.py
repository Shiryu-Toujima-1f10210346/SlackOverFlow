from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# QdrantとOpenAIの設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
QDRANT_HOST = os.getenv("QDRANT_HOST")
PORT = int(os.getenv("PORT"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

def load_qdrant():
    embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_API_BASE)
    
    client = QdrantClient(host=QDRANT_HOST, port=PORT)

    # すべてのコレクション名を取得
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]

    # コレクションが存在しなければ作成
    if COLLECTION_NAME not in collection_names:
        # コレクションが存在しない場合、新しく作成
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        print('collection created')
    
    return Qdrant(
        client=client,
        collection_name=COLLECTION_NAME, 
        embeddings=embeddings_model
    )