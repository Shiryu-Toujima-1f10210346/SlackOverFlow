from django.shortcuts import render
from django.http import JsonResponse
from .slack_client import get_all_channel_history
from .rag import build_rag_retriever, get_answer

# グローバル変数としてリトリーバーを保持
retriever = None

def index(request):
    """
    インデックスページのレンダリング
    """
    return render(request, 'chatbot/index.html')

def build_rag_view(request):
    """
    RAGの構築を行うビュー関数
    """
    global retriever
    try:
        # Slackの会話履歴を取得
        history = get_all_channel_history()
        # 取得した履歴を基にRAGのリトリーバーを構築
        retriever = build_rag_retriever(history)
        return JsonResponse({'status': 'RAGを構築しました'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_answer_to_view(request):
    """
    質問に基づいてRAGを使用して応答するビュー関数
    """
    global retriever
    if retriever is None:
        return JsonResponse({'error': 'RAGがまだ構築されていません。'}, status=400)

    if request.method == 'POST':
        try:
            # リクエストから質問を取得
            question = request.POST.get('question')
            if not question:
                return JsonResponse({'error': '質問が提供されていません。'}, status=400)

            # RAGを使用して質問に対する回答を取得
            answer = get_answer(question, retriever)
            return JsonResponse({'answer': answer})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'POSTリクエストのみが許可されています。'}, status=405)

