from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .qdrant_setup import load_qdrant
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
import os
from .slack_client import get_all_channel_history
from langchain_community.vectorstores import Qdrant
from dotenv import load_dotenv


# .envファイルから環境変数を読み込む
load_dotenv()

# QdrantとOpenAIの設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
QDRANT_HOST = os.getenv("QDRANT_HOST")
PORT = int(os.getenv("PORT"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
# ChatGPTのモデルを定義
llm = ChatOpenAI(
    model_name="gpt-4o-mini",  # 使用するモデル
    temperature=0,  # 出力の多様性を制御する温度パラメータ
    openai_api_base=OPENAI_API_BASE,  # OpenAI APIのベースURL
    verbose=True
)

# プロンプトテンプレートの定義
template = """Answer the question based only on the following context:

{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    """ ドキュメントをフォーマットするためのヘルパー関数 """
    return "\n\n".join([d.page_content for d in docs])

def build_rag_chain():
    """RAGのチェーンを構築し、ユーザーの質問に応答するための関数"""
    
    # Retrieverを構築
    retriever = load_qdrant().as_retriever(search_type="mmr", k=10, verbose=True)

    # RAGのチェーンの定義
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser(verbose=True)
    )
    
    return chain

def get_answer(question):
    """ ユーザーの質問に対してRAGチェーンを使用して回答を生成する関数 """
    # RAGチェーンを構築
    chain = build_rag_chain()
    
    # 質問に対して回答を生成
    answer = chain.invoke(question)
    
    return answer

def build_rag_retriever():
    # Qdrantのセットアップ
    qdrant = load_qdrant()

    # OpenAIの埋め込みモデルのインスタンスを作成
    embeddings_model = OpenAIEmbeddings(openai_api_base=OPENAI_API_BASE, openai_api_key=OPENAI_API_KEY)

    # テキストスプリッタの設定
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,  # チャンクのサイズ
        chunk_overlap=100,  # チャンク間のオーバーラップ
        length_function=len,
        add_start_index=True
    )

    # Slackの会話履歴を取得
    # slack_client.pyのget_all_channel_history関数を使用
    all_history = get_all_channel_history()

    # 取得した会話を一つのテキストに結合
    all_text = " ".join([f"[name:{h['display_name']}, message:{h['text']}, time:{h['ts']}]" for h in all_history])
    all_text = all_text.replace("\n", " ")  # 改行をスペースに変換

    # テキストをチャンクに分割
    documents = text_splitter.create_documents([all_text])

    # 各チャンクにメタデータを追加
    for doc in documents:
        doc.metadata = {'source': 'slack'}

    # Qdrantにチャンクを追加
    qdrant.add_texts(texts=[doc.page_content for doc in documents], metadatas=[doc.metadata for doc in documents])

    # ベクトルストアからの検索用のretrieverを返す
    retriever = qdrant.as_retriever(search_type="mmr", k=10, verbose=True)
    
    return retriever