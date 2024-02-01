from django.urls import path
from .views import LearnChatbotView

urlpatterns = [
    path('', LearnChatbotView.as_view(), name='learn_chatbot'),
]