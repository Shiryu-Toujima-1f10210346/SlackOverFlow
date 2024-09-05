from django.shortcuts import render
from django.http import JsonResponse
from .slack_client import get_all_channel_history
from .rag import build_rag_retriever, get_answer

def index(request):
    # インデックスページのレンダリング
    return render(request, 'chatbot/index.html')

def get_slack_conversation(request):
    # Slackの会話履歴を取得
    history = get_all_channel_history()
    return JsonResponse({'history': history})

# retrieverオブジェクトの初期化
retriever = build_rag_retriever()

def get_answer_to_view(request):
    question = request.GET.get('question')
    if question:
        reference = retriever.get_relevant_documents(question)
        print(reference)
        answer = get_answer(question)
        return JsonResponse({'answer': answer, 'reference': str(reference)})
        # return JsonResponse({'answer': answer})
    return JsonResponse({'error': 'No question provided'})
