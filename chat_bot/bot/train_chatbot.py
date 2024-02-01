import os

import nltk
# from keras.src.optimizers import SGD
import keras
from nltk.stem import WordNetLemmatizer


import json
import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
import random
import time

words = []
classes = []
documents = []
ignore_words = ['?', '!', ',']
data_file = open('chat_bot/intents.json').read()
intents = json.loads(data_file)
lemmatizer = WordNetLemmatizer()
for intent in intents['intents']:
    for pattern in intent['patterns']:
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        documents.append((w, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

print(len(documents), "documents")
print(len(classes), "classes", classes)
print(len(words), "unique lemmatized words", words)
pickle.dump(words, open('../words.pkl', 'wb'))
pickle.dump(classes, open('../classes.pkl', 'wb'))

output_empty = [0] * len(classes)
training = []

for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]

    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)
training = np.array(training, dtype=object)
train_x = [x[0] for x in training]
train_y = [x[1] for x in training]
train_x = np.array(train_x)
train_y = np.array(train_y)

print("Training data created")

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))
# Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
# sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
# model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

adam = keras.optimizers.Adam(0.001)
model.compile(optimizer=adam, loss='categorical_crossentropy', metrics=['accuracy'])


def train_chatbot():
    hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
    # model.save('chatbot_model.h5', hist)
    model.save('../chatbot_model.keras', hist)
    print("model created")

# def check_json_changes():
#     # Get the last modification time of the JSON file
#     last_modified = os.path.getmtime('intents.json')
#     # Check if the file has been updated since the last check
#     if last_modified != check_json_changes.last_modified:
#         # Update the last modified timestamp
#         check_json_changes.last_modified = last_modified
#         # Call the function to retrain the chatbot
#         train_chatbot()
#
# # Run training loop indefinitely with a sleep interval of 1 hour
# while True:
#     train_chatbot()
#     time.sleep(3600)  # Sleep for 1 hour (3600 seconds)
