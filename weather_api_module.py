import requests

class WeatherAPI:
    def __init__(self, cidade="Porto Alegre", dias=3):
        # Armazena os parâmetros padrão e carrega a previsão do tempo
        self.cidade = cidade
        self.dias = dias
        self.clima = self.request(self.cidade, self.dias)

    def request(self, cidade, dias):
        # Monta a consulta para a API
        querystring = {"q": cidade, "days": dias}
        url = "https://weatherapi-com.p.rapidapi.com/current.json"
        headers = {
            "x-rapidapi-key": "9a16e0eb17msh75d1d55a14979a0p1e60c9jsnfa7bc76edbf9",
            "x-rapidapi-host": "weatherapi-com.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        return response.json()

    def get_data(self):
        # Extrai os dados do JSON e imprime as informações
        nome_cidade = self.clima['location']['name']
        temperatura_c = self.clima['current']['temp_c']
        condicao_climatica = self.clima['current']['condition']['text']
        vento_kph = self.clima['current']['wind_kph']
        umidade = self.clima['current']['humidity']
        return nome_cidade, temperatura_c, condicao_climatica, vento_kph, umidade

    def atualizar_previsao(self, nova_cidade=None, novos_dias=None):
        # Atualiza a cidade e/ou dias, se fornecidos
        if nova_cidade:
            self.cidade = nova_cidade
        if novos_dias:
            self.dias = novos_dias
        # Recarrega os dados do clima com base nos novos parâmetros
        self.clima = self.request(self.cidade, self.dias)