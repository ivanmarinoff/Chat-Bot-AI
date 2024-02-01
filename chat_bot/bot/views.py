import nltk
from Scripts.bottle import response
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from nltk.stem import WordNetLemmatizer
import webbrowser
import requests
from pycricbuzz import Cricbuzz
import billboard
import time
from pygame import mixer
import COVID19Py
import pickle
import numpy as np
from keras.models import load_model
import json
import random
from regex import search

lemmatizer = WordNetLemmatizer()
model = load_model('chat_bot/chatbot_model.keras')
intents = json.loads(open('chat_bot/intents.json').read())
words = pickle.load(open('chat_bot/words.pkl', 'rb'))
classes = pickle.load(open('chat_bot/classes.pkl', 'rb'))


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)

    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return (np.array(bag))


def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []

    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(return_list, intents_json):
    # tag = ints[0]['intent']
    # list_of_intents = intents_json['intents']
    # for i in list_of_intents:
    #     if (i['tag'] == tag):
    #         result = random.choice(i['responses'])
    #         break
    # return result
    if len(return_list) == 0:
        tag = 'noanswer'
    else:
        tag = return_list[0]['intent']

    if tag == 'datetime':
        return time.strftime("%d %B %Y %A %H:%M:%S")
        # print(time.strftime("%A"))
        # print(time.strftime("%d %B %Y"))
        # print(time.strftime("%H:%M:%S"))

    # if tag == 'google':
    #     query = []
    #     chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe %s'
    #
    #     for url in search(query, tld="co.in", num=10, stop=10, pause=2):
    #         webbrowser.open("https://google.com/search?q=%s" % query)
    #         return str(url)


    # if tag == 'weather':
    #     api_key = ''
    #     base_url = "http://api.openweathermap.org/data/2.5/weather?"
    #     city_name = input("Enter city name : ")
    #     complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    #     response = requests.get(complete_url)
    #     x = response.json()
    #     print('Present temp.: ', round(x['main']['temp'] - 273, 2), 'celcius ')
    #     print('Feels Like:: ', round(x['main']['feels_like'] - 273, 2), 'celcius ')
    #     print(x['weather'][0]['main'])

    if tag == 'news':
        # main_url = " http://newsapi.org/v2/top-headlines?country=us&apiKey=bc88c2e1ddd440d1be2cb0788d027ae2"
        main_url = " http://newsapi.org/v2/everything?domains=wsj.com&apiKey=bc88c2e1ddd440d1be2cb0788d027ae2"
        open_news_page = requests.get(main_url).json()
        article = open_news_page["articles"]
        results = []

        for ar in article:
            results.append([ar["title"], ar["url"]])

        for i in range(10):
            # print(i + 1, results[i][0])
            result = i + 1
            return str(result) + '. ' + results[i][0]
            # print(results[i][1], '\n')

    # if tag == 'cricket':
    #     c = Cricbuzz()
    #     matches = c.matches()
    #     for match in matches:
    #         print(match['srs'], ' ', match['mnum'], ' ', match['status'])

    if tag == 'song':
        chart = billboard.ChartData('hot-100')
        print('The top 10 songs at the moment are:')
        for i in range(10):
            song = chart[i]
            # print(song.title, '- ', song.artist)
            return str(i + 1) + '. ' + song.title + ' - ' + song.artist

    if tag == 'timer':
        mixer.init()
        # x = input('Minutes to timer..')
        x = 5
        time.sleep(float(x) * 60)
        mixer.music.load('Handbell-ringing-sound-effect.mp3')
        mixer.music.play()

    # if tag == 'covid19':
    #
    #     covid19 = COVID19Py.COVID19(data_source='jhu')
    #     country = input('Enter Location...')
    #
    #     if country.lower() == 'world':
    #         latest_world = covid19.getLatest()
    #         print('Confirmed:', latest_world['confirmed'], ' Deaths:', latest_world['deaths'])
    #
    #     else:
    #
    #         latest = covid19.getLocations()
    #
    #         latest_conf = []
    #         latest_deaths = []
    #         for i in range(len(latest)):
    #
    #             if latest[i]['country'].lower() == country.lower():
    #                 latest_conf.append(latest[i]['latest']['confirmed'])
    #                 latest_deaths.append(latest[i]['latest']['deaths'])
    #         latest_conf = np.array(latest_conf)
    #         latest_deaths = np.array(latest_deaths)
    #         print('Confirmed: ', np.sum(latest_conf), 'Deaths: ', np.sum(latest_deaths))

    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if tag == i['tag']:
            result = random.choice(i['responses'])
    return result


def chatbot_view(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if message:
            ints = predict_class(message, model)
            res = getResponse(ints, intents)
            return render(request, 'chatbot.html', {'response': res})
        else:
            return render(request, 'chatbot.html', {'error': 'Message field is required.'})
    else:
        return render(request, 'chatbot.html')


# while (1):
#     x = input()
#     print(response(x))
#     if x.lower() in ['bye', 'goodbye', 'get lost', 'see you']:
#         break

# Self learning
# print('Help me Learn?')
# tag = input('Please enter general category of your question  ')
# flag = -1
# for i in range(len(intents['intents'])):
#     if tag.lower() in intents['intents'][i]['tag']:
#         intents['intents'][i]['patterns'].append(input('Enter your message: '))
#         intents['intents'][i]['responses'].append(input('Enter expected reply: '))
#         flag = 1
#
# if flag == -1:
#     intents['intents'].append(
#         {'tag': tag,
#          'patterns': [input('Please enter your message')],
#          'responses': [input('Enter expected reply')]})
#
# with open('intents.json', 'w') as outfile:
#     outfile.write(json.dumps(intents, indent=4))

