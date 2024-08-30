import json
import numpy as np
import datetime
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# Função de tokenização personalizada
def custom_tokenizer(text):
    return text.split()

# Função para carregar os dados do arquivo JSON
def load_intents(filename):
    with open(filename, 'r', encoding='utf-8-sig') as file:
        return json.load(file)

# Função para pré-processar os dados e treinar o modelo
def train_model(intents, model_filename="chatbot_model.pkl", vectorizer_filename="vectorizer.pkl", encoder_filename="encoder.pkl"):
    patterns = []
    tags = []

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            patterns.append(pattern)
            tags.append(intent['tag'])

    # Transformar os padrões em vetores numéricos
    vectorizer = TfidfVectorizer(tokenizer=custom_tokenizer, stop_words='english', ngram_range=(1, 2))
    #vectorizer = TfidfVectorizer(tokenizer=custom_tokenizer, stop_words='english')
    X = vectorizer.fit_transform(patterns).toarray()

    # Codificar as tags
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(tags)

    # Dividir os dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Criar e treinar o modelo SVM
    #model = SVC(kernel='linear', probability=True)
    #model = SVC(kernel='linear', C=1.4, probability=True)
    model = SVC(kernel='linear', C=1.5, probability=True)


    model.fit(X_train, y_train)

    # Avaliar o modelo
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")

    # Salvar o modelo, o vetorizador e o codificador de tags
    with open(model_filename, 'wb') as model_file:
        pickle.dump(model, model_file)
    with open(vectorizer_filename, 'wb') as vectorizer_file:
        pickle.dump(vectorizer, vectorizer_file)
    with open(encoder_filename, 'wb') as encoder_file:
        pickle.dump(label_encoder, encoder_file)

    print("Modelo treinado e salvo com sucesso.")

# Função para carregar o modelo, vetorizador e codificador
def load_model(model_filename="chatbot_model.pkl", vectorizer_filename="vectorizer.pkl", encoder_filename="encoder.pkl"):
    with open(model_filename, 'rb') as model_file:
        model = pickle.load(model_file)
    with open(vectorizer_filename, 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    with open(encoder_filename, 'rb') as encoder_file:
        label_encoder = pickle.load(encoder_file)
    return model, vectorizer, label_encoder

# Funções para comandos específicos
def comando_hora():
    return datetime.datetime.now().strftime("%H:%M:%S")

def comando_data():
    return datetime.datetime.now().strftime("%d/%m/%Y")

def comando_clima():
    return "Hoje vai chover"

# Função para prever a classe/tag da entrada do usuário
def predict_class(text, model, vectorizer, label_encoder):
    text_vector = vectorizer.transform([text]).toarray()
    predicted_tag = model.predict(text_vector)[0]
    return label_encoder.inverse_transform([predicted_tag])[0]

# Função para obter a resposta com base na tag prevista
def get_response(intents, tag):
    if tag == "hora":
        return comando_hora()
    elif tag == "data":
        return comando_data()
    elif tag == "clima":
        return comando_clima()
    else:
        for intent in intents['intents']:
            if intent['tag'] == tag:
                return np.random.choice(intent['responses'])

# Função de interação com o usuário
def chat(intents, model, vectorizer, label_encoder):
    while True:
        input_text = input("Você: ")
        if input_text.lower() == "sair":
            break
        predicted_tag = predict_class(input_text, model, vectorizer, label_encoder)
        response = get_response(intents, predicted_tag)
        print(f"Bot: {response}")



treinar = True
treinar = False

if treinar:
    intents = load_intents('intents.json')
    train_model(intents)
else:
    intents = load_intents('intents.json')
    model, vectorizer, label_encoder = load_model()
    chat(intents, model, vectorizer, label_encoder)

