import requests

class Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"

    #Metodo che effettua una richiesta per ottenere gli aggiornamenti (messaggi, azioni dell'utente...)
    def get_updates(self, offset=None):
        method = "getUpdates"
        params = {'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result = resp.json()
        return result

    #Questo metodo invia un messaggio a un certo chat_id (identificativo della chat su Telegram) con un testo specificato.
    def send_message(self, chat_id, text):
        method = "sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        resp = requests.post(self.api_url + method, params).json()
        return resp