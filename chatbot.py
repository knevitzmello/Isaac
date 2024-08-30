import random
import json
import pickle
import numpy as np
from datetime import datetime
import os
import locale
from weather_api_module import WeatherAPI
from deep_translator import GoogleTranslator

locale.setlocale(locale.LC_TIME, 'pt_BR')

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import nltk
from nltk.stem import WordNetLemmatizer

import tensorflow as tf


lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json', encoding='utf-8').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = tf.keras.models.load_model('chatbot_model.keras')
tradutor_en_pt = GoogleTranslator(source= "en", target= "pt")

weather = WeatherAPI()


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    if len(intents_list) == 0: tag = ["nao_entendi"]
    else: tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = parse_command(random.choice(i['responses']))
            break
        else: result = "Não entendi"
    return result

def parse_command(result):
    match result:
        case "Comando 1":
            hora_atual = datetime.now()
            horario_formatado = hora_atual.strftime("%H:%M")
            return "Agora é " + horario_formatado
        case "Comando 2":
            data_atual = datetime.now()
            data_formatada = data_atual.strftime(f"%A, dia %d de %B de %Y")
            return "Hoje é " + data_formatada
        case "Comando 3":
            data_atual = datetime.now()
            data_formatada = data_atual.strftime("%A, dia %d de %B de %Y")
            nome_cidade, temperatura_c, condicao_climatica, vento_kph, umidade = weather.get_data()
            condicao_climatica = tradutor_en_pt.translate(condicao_climatica)
            info_clima = (
                f"Atualmente em {nome_cidade}, a temperatura é de {temperatura_c}°C "
                f"com céu {condicao_climatica}. A velocidade do vento está em {vento_kph} km/h "
                f"e a umidade relativa do ar é de {umidade}%."
            )
            return info_clima
    return result

print("bot rodando...")

while True:
    message = input("")
    ints = predict_class(message)
    res = get_response(ints, intents)
    print(res)