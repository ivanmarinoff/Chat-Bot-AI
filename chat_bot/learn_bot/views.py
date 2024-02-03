from threading import Timer

from django.views.generic import View
import json
from django.shortcuts import render
from django.http import JsonResponse

from chat_bot.bot.train_chatbot import train_chatbot
from chat_bot.bot.views import intents


class LearnChatbotView(View):
    def get(self, request):
        return render(request, 'learn.html')

    def post(self, request):
        data = json.loads(request.body)
        tag = data.get('tag', '').lower()
        message = data.get('message', '')
        reply = data.get('reply', '')

        flag = False
        for intent in intents['intents']:
            if tag == intent['tag'].lower():
                intent['patterns'].append(message)
                intent['responses'].append(reply)
                flag = True
                break

        if not flag:
            intents['intents'].append({
                'tag': tag,
                'patterns': [message],
                'responses': [reply]
            })

        with open('chat_bot/intents.json', 'w', encoding='utf-8') as outfile:
            json.dump(intents, outfile, ensure_ascii=False, indent=4)

        for i in self.check_tag_yield(tag):
            Timer(5, train_chatbot).start()

        return JsonResponse({'message': f'Learning with tag {tag} completed successfully'}, status=200)

    def find_tag_index(self, tag):
        """Find the index of the intent with the given tag."""
        for i, intent in enumerate(intents['intents']):
            if tag == intent['tag'].lower():
                return i
        return None

    def check_tag_yield(self, tag):
        """Check if the JSON file contains a tag with the newly added word and yield its index."""
        for i, intent in enumerate(intents['intents']):
            if tag == intent['tag'].lower():
                yield i
