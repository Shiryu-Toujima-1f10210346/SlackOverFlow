
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os

#APIキーの登録
os.environ["OPENAI_API_KEY"] = "oKkn1f08fSdP890mnZW6qI4XBbacIj4sSgJMyfnG7yGzqrNMRZs8DNLkNuAOKq-LjmliGRhE8z00ik39j4s_OAQ"

url = "https://api.openai.iniad.org/api/v1/"

# OpenAI埋め込みモデルのインスタンスを作成
embeddings_model = OpenAIEmbeddings(
    openai_api_base= url
)

# 以下の日本語をOPENAIのEnbeddingを使ってベクトル化する
embeddings = embeddings_model.embed_documents(
    [
        "鬼滅の刃は週刊少年ジャンプにて掲載中の人気の漫画だ",
        "マウリヤ朝は人々の漫遊な生活とシュンガ朝の勃興により滅亡した",
        "ルフィが活躍するマンガのワンピースは売上が１億冊を超えた",
        "ルマンドは１ピースあたり９８グラムである"
    ]
)
# len(embeddings) は文書の数を、len(embeddings[0]) は各文書の埋め込みベクトルの次元数を表している
len(embeddings), len(embeddings[0])
print(embeddings[0])