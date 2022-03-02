import random
import json
import pyttsx3
import torch
import speech_recognition as sr
import mysql.connector

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('../../PycharmProjects/pythonProject2/intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "../../PycharmProjects/pythonProject2/data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
# print(voices[1].id)
engine.setProperty('rate', 150)
# engine.say("Hello, How are you ?")
engine.runAndWait()


def speak(sentence):
    engine.say(sentence)
    engine.runAndWait()


bot_name = "Friday"
speak("Hi ")

r = sr.Recognizer()
while True:
    # sentence = "do you use credit cards?
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source)
        try:
            convo = r.recognize_google(audio)
            sentence = convo
        except:
            continue

        if sentence == "quit":
            speak("Bye, have a nice day")
            break

        sentence = tokenize(sentence)
        X = bag_of_words(sentence, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)

        output = model(X)
        _, predicted = torch.max(output, dim=1)

        tag = tags[predicted.item()]

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]
        if prob.item() > 0.75:
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    speak(f"{random.choice(intent['responses'])}")

        else:
            speak("what does that mean")
            audi = r.listen(source)
            reply = r.recognize_google(audi)

            speak("okay, got it")
            speak(f"so what you said is {reply}")

            print(convo)
            print(reply)
            try:
                mydb = mysql.connector.connect(host="localhost", user="root", password="", database="face_rec")

                mycursor = mydb.cursor()
                cur = "INSERT INTO chat(patterns, responses) VALUES(%s,%s)"
                res = [convo, reply]
                mycursor.execute(cur, res)
                mydb.commit()

            except:
                print("Database connection exception!")
