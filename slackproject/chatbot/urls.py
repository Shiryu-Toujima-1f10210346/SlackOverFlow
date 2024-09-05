from django.urls import path
from . import views,slack_client

urlpatterns = [
    path('', views.index, name='index'),  # インデックスページ
    path('get_slack_conversation/', slack_client.get_all_channel_history, name='get_all_channel_history'),
    path('get_answer/', views.get_answer_to_view, name='get_answer_to_view'),
    path('build_rag/', views.build_rag_view, name='build_rag_view'),
]
