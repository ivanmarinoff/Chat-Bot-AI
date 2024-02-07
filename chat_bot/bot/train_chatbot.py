import os
import random

import nltk
import keras
import json
import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from nltk.stem import WordNetLemmatizer
from chat_bot.settings import data_file


class ChatbotTrainer:
    def __init__(self):
        self.words = []
        self.classes = []
        self.documents = []
        self.ignore_words = ['?', '!', ',']
        self.intents = json.loads(data_file)
        self.lemmatizer = WordNetLemmatizer()

    def preprocess_data(self):
        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                w = nltk.word_tokenize(pattern)
                self.words.extend(w)
                self.documents.append((w, intent['tag']))
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

        self.words = [self.lemmatizer.lemmatize(w.lower()) for w in self.words if w not in self.ignore_words]
        self.words = sorted(list(set(self.words)))
        self.classes = sorted(list(set(self.classes)))

    def create_training_data(self):
        output_empty = [0] * len(self.classes)
        training = []

        for doc in self.documents:
            bag = []
            pattern_words = doc[0]
            pattern_words = [self.lemmatizer.lemmatize(word.lower()) for word in pattern_words]

            for w in self.words:
                bag.append(1) if w in pattern_words else bag.append(0)
            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1
            training.append([bag, output_row])

        random.shuffle(training)
        training = np.array(training, dtype=object)
        train_x = [x[0] for x in training]
        train_y = [x[1] for x in training]
        train_x = np.array(train_x)
        train_y = np.array(train_y)

        return train_x, train_y

    def train_chatbot(self):
        self.preprocess_data()
        train_x, train_y = self.create_training_data()

        model = Sequential()
        model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(len(train_y[0]), activation='softmax'))

        adam = Adam(0.001)
        model.compile(optimizer=adam, loss='categorical_crossentropy', metrics=['accuracy'])

        hist = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)
        model.save('../chatbot_model.keras', hist)
        print("Model created successfully.")


if __name__ == "__main__":
    trainer = ChatbotTrainer()
    trainer.train_chatbot()