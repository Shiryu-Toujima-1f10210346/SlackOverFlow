from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # インデックスページ
    path('get_slack_conversation/', views.get_slack_conversation, name='get_slack_conversation'),
    path('get_answer/', views.get_answer_to_view, name='get_answer_to_view'),
]
