from django.urls import path
from chat_bot.bot.views import chatbot_view

urlpatterns = [
    path('', chatbot_view, name='chatbot'),
]
