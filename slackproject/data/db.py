
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
os.environ["OPENAI_API_KEY"] = "OpenAIのAPIkeyを入力してね"

# Slack APIトークン
slack_token = "SlackのAPIトークンを入力してね"

# WebClientのインスタンスを作成
client = WebClient(token=slack_token)
import os


url = "https://api.openai.iniad.org/api/v1/"

def get_all_channel_history():
    all_history = []  # 全ての履歴を保存するリスト

    # ユーザーリストを取得
    users = client.users_list()['members']
    user_map = {}
    for user in users:
      user_map[user['id']] = user['profile']['display_name']

    try:
        # 全チャンネルを取得
        channels = client.conversations_list()['channels']

        # 各チャンネルで会話履歴を取得
        for channel in channels:
            channel_id = channel['id']
            channel_name = channel['name']

            try:
                # 会話履歴の取得
                response = client.conversations_history(channel=channel_id)
                messages = response['messages']

                # 各メッセージにチャンネル名を追加して保存
                for message in messages:
                    user_id = message.get('user', 'システム')
                    display_name = user_map.get(user_id, user_id)
                    all_history.append({
                        'channel': channel_name,
                        # 'user': message.get('user', 'システム'),
                        'display_name': display_name,
                        'text': message.get('text', ''),
                        'ts': message.get('ts')  # タイムスタンプを保存しておく
                    })

            except SlackApiError as e:
                print(f"チャンネル '{channel_name}' での会話履歴取得エラー: {e.response['error']}")

    except SlackApiError as e:
        print(f"チャンネル一覧の取得エラー: {e.response['error']}")

    return all_history

# 全チャンネルの会話履歴を取得して保存
all_history = get_all_channel_history()

# 会話履歴のサンプルを表示
for history in all_history[:5]:
    print(f"チャンネル: {history['channel']} | ユーザー: {history['display_name']} | メッセージ: {history['text']} | タイムスタンプ: {history['ts']}")


# Chromaにドキュメントを追加
# Text Splitterの設定（チャンクサイズとオーバーラップを指定）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024,
    chunk_overlap=100,
    length_function=len,
    add_start_index=True
)

all_documents = []

# 各チャンネルの会話履歴を個別にチャンク化
for channel in client.conversations_list()['channels']:
    channel_id = channel['id']
    channel_name = channel['name']

    try:
        # 会話履歴全体を一つの文字列として結合
        all_text = " ".join([f"[name:{h['display_name']}, message:{h['text']}, time:{h['ts']}]" for h in all_history])
        all_text = all_text.replace("\n", " ")

        # テキストをチャンクに分割
        documents = text_splitter.create_documents([all_text])

        # 各チャンクにメタデータを追加
        for doc in documents:
            doc.metadata = {
                'channel': channel_name,
            }
        all_documents.extend(documents)

    except SlackApiError as e:
        print(f"チャンネル '{channel_name}' での会話履歴取得エラー: {e.response['error']}")

embeddings_model = OpenAIEmbeddings(
    openai_api_base= url
)

db = Chroma.from_documents(all_documents, embeddings_model)

# retriever(検索対象のVectorDB)の定義
retriever = db.as_retriever()

# テンプレートを定義
template = """Answer the question based only on the following context:

{context}

Question: {question}
"""
# promptを定義。これがLLMの入力になる
prompt = ChatPromptTemplate.from_template(template)

# LLMを定義。今回はChatGPTの4o-miniを利用する
llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    openai_api_base= url,
    verbose=True
    )


def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

# Chainを定義。これはおまじないだと思って下さい。
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser(verbose=True)
    )

# OpenAI埋め込みモデルのインスタンスを作成
embeddings_model = OpenAIEmbeddings(
    openai_api_base= url
)

import gradio as gr

def get_answer(question):
  references = retriever.get_relevant_documents(question)
  output_by_retriever = chain.invoke(question)
  return output_by_retriever, references


iface = gr.Interface(
    fn=get_answer,
    inputs=gr.Textbox(lines=2, placeholder="質問を入力してください"),
    outputs=[
        gr.Textbox(lines=5, label="回答"),
        gr.Textbox(lines=5, label="参考にした箇所")
    ],
    title="Slack RAG",
    description="Slackの会話履歴から回答を生成します"
)

iface.launch()
