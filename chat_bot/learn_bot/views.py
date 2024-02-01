from django.views.generic import View
import json
from django.shortcuts import render
from django.http import JsonResponse
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

        # with open('intents.json', 'r') as infile:
        #     intents = json.load(infile)

        return JsonResponse({'message': f'Learning wit tag {tag} completed successfully'}, status=200)
