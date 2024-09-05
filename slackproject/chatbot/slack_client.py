from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import os

# Slack APIトークンとクライアント設定
load_dotenv()
slack_token = os.getenv('SLACK_API_TOKEN')
client = WebClient(token=slack_token)
print('Slack APIトークン:', slack_token)
print('OPenAI APIトークン:', os.getenv('OPENAI_API_KEY'))

def get_all_channel_history():
    # Slackから全チャンネルの会話履歴を取得する処理
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
                        'display_name': display_name,
                        'text': message.get('text', ''),
                        'ts': message.get('ts')  # タイムスタンプを保存
                    })

            except SlackApiError as e:
                print(f"チャンネル '{channel_name}' での会話履歴取得エラー: {e.response['error']}")

    except SlackApiError as e:
        print(f"チャンネル一覧の取得エラー: {e.response['error']}")

    return all_history
