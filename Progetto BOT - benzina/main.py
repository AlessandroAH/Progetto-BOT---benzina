import math
import re
import sys
import requests
from bot import Bot
from db import DataBase
import json

#Inizializzazione bot e db
bot = Bot("6949498361:AAGdysoT7C9uMgWlwxlS-FcgSJwXKQwQeNw")
db = DataBase("localhost", "root", "", "db_benzinai")
#Variabili utili
dati_utente = ["","","","","",""]    #[0]chat_id, [1]nome, [2]tipo carburante, [3]capacità, [4]maxKm (per arrivare al benzinaio più vicino), [5]posizione attuale
last_update_id = 0

def main():
    print("Inizio programma")
    
    text=""
    
    while True:
        global last_update_id
    
        response = bot.get_updates(last_update_id)      #va a vedere l'ultimo messaggio ricevuto con offset = last_update_id
        print(response)
        
        #Controllo se qualcuno ha scritto qualcosa
        if len(response['result']) > 0:                                         #se c'è un nuovo messaggio
            last_update_id = response['result'][0]['update_id'] + 1             #da al nuovo messaggio un id
            try:
                text = response['result'][0]['message']['text']
            except:
                text = ""
            dati_utente[0] = response['result'][0]['message']['chat']['id']
                     
        if text == "/start":
            inizia_chat()

def inizia_chat():
    global dati_utente
    
    bot.send_message(dati_utente[0], "Ciao sono il bot benzinaio!")         #dati_utente[0] = chat_id [che server per inviare il messaggio a il messaggio con quell'ID]
    
    #Faccio le domande e prendo il tipo di benzinaio che vuole l'utente ovvero se uno vicno o economico
    tipo_benzinaio = domandeBenzina()
    
    #Cerco il benzinaio richiesto dalle domande fatte e ritorno la lista dei benzinai
    benzinaioEntroRaggio = ricercaBenzinaio()
    
    #calcoli...
    latitudine_utente,longitudine_utente = estraiLatLong(dati_utente[5])        
    punto = (latitudine_utente, longitudine_utente)
    min = sys.maxsize
    
    if tipo_benzinaio == 'vicino':
        for benzinaio in benzinaioEntroRaggio:
            distanza = haversine(punto[0], punto[1], benzinaio[1], benzinaio[2])
            if distanza < min:
                benzinaio_piu_vicino = benzinaio
                min = distanza
                
        bot.send_message(dati_utente[0], "Il benzinaio più vicino è " + benzinaio_piu_vicino[0] + " con un prezzo di " + str(benzinaio_piu_vicino[3]) + "€" + " all'indirizzo " + str(benzinaio_piu_vicino[4]) + " nel comune di " + str(benzinaio_piu_vicino[5]))
    elif tipo_benzinaio == 'economico':
        for benzinaio in benzinaioEntroRaggio:
            distanza = haversine(punto[0], punto[1], benzinaio[1], benzinaio[2])
            if benzinaio[3] < min:
                benzinaio_piu_vicino = benzinaio
                min = benzinaio[3]
        bot.send_message(dati_utente[0], "Il benzinaio più economico è " + benzinaio_piu_vicino[0] + " con un prezzo di " + str(benzinaio_piu_vicino[3]) + "€" + " all'indirizzo " + str(benzinaio_piu_vicino[4]) + " nel comune di " + str(benzinaio_piu_vicino[5]))
        
#Metodi domande e ricerca
   
def domandeBenzina():
    global dati_utente
    
    #Domanda del nome
    bot.send_message(dati_utente[0], "Come ti chiami?")
    data = getRisposta()
    dati_utente[1] = data['result'][0]['message']['text']
    
    #Domanda del tipo di carburante
    bot.send_message(dati_utente[0], dati_utente[1] + ", che tipo di carburante vuoi (Benzina/Gasolio/Metano/GPL/Blue Diesel...)?")
    data = getRisposta()
    dati_utente[2] = data['result'][0]['message']['text']
    
    #Domanda della capacità del serbatoio
    #Non capisco a che cosa serve
    bot.send_message(dati_utente[0], "Inserisci la capacità del serbatoio?")
    data = getRisposta()
    dati_utente[3] = data['result'][0]['message']['text']
    
    #Domanda del maxKm che percorreresti per fare rifornimento
    bot.send_message(dati_utente[0], "Inserisci il maxKm che percorreresti per fare rifornimento?")
    data = getRisposta()
    dati_utente[4] = data['result'][0]['message']['text']
    
    #Domanda della posizione attuale
    bot.send_message(dati_utente[0], "Mandami la tua posizione")
    data = getRisposta()
    # Verifica se il messaggio contiene la posizione
    if 'location' in data['result'][0]['message']:
        # Estrai la longitudine e la latitudine dalla posizione
        location = data['result'][0]['message']['location']
        longitude = location['longitude']
        latitude = location['latitude']

        # Ora puoi utilizzare longitude e latitude come necessario
        print(f"Longitudine: {longitude}, Latitudine: {latitude}")

        # Assegna i valori a dati_utente[4] o a qualsiasi altra variabile secondo necessità
        dati_utente[5] = f"Longitudine:{longitude}, Latitudine:{latitude}"
    else:
        # Gestisci il caso in cui la posizione non sia presente nel messaggio
        print("Il messaggio non contiene informazioni sulla posizione")
    
    #Partono le scelte da fare al utente
    
    #Domanda se vuole il distributore più vicino o più economico
    bot.send_message(dati_utente[0], 'Distributore più vicino o distributore più economico? (vicino/economico)')
    InviaScelte(dati_utente[0], ['Vicino', 'Economico'])
    data = getRisposta()
    tipoBenzinaio = data['result'][0]['message']['text'].lower()

    return tipoBenzinaio        
    
    #DOMANDA INUTILE
    #Quanta ne vuole fare
    #bot.send_message(dati_utente[0], 'Quanta benzina vuoi? (1/4, 2/4, 3/4, 4/4))')
    #InviaScelte(dati_utente[0], ['1/4', '2/4', '3/4', '4/4'])
    #data = getRisposta()
    #quantita = data['result'][0]['message']['text']
    
    #ALLA FINE DI TUTTE LE DOMANDE NEL DATI_UTENTE HO TUTTI I DATI CHE MI SERVONO PER FARE LA QUERY
  
def ricercaBenzinaio(): 
    #Faccio la query al DB
    query = "SELECT anagrafica.nome, anagrafica.Latitudine, anagrafica.Longitudine, prezzi.Prezzo, anagrafica.Indirizzo, anagrafica.Comune FROM prezzi JOIN anagrafica on prezzi.IDImpianto = anagrafica.ID WHERE TipoCarburante = '" + dati_utente[2] + "'"
    result = db.esegui_query(query)
    
    # Inizializza un vettore per salvare i dati di ogni benzinaio
    benzinai_dati = []
    punto = []
    benzinai_entro_raggio = []

    # Itera sui risultati della query e salva i dati di ogni benzinaio nel vettore
    for row in result:
        nome_benzinaio = row[0]
        latitudine_benzinaio = float(row[1])
        longitudine_benzinaio = float(row[2])
        prezzo_benzinaio = float(row[3])
        indirizzo_benzinaio = row[4]
        comune_benzinaio = row[5]

        #print(f"Nome: {nome_benzinaio}, Latitudine: {latitudine_benzinaio}, Longitudine: {longitudine_benzinaio}")
        
        # Aggiungi i dati al vettore
        benzinai_dati.append((nome_benzinaio, latitudine_benzinaio, longitudine_benzinaio, prezzo_benzinaio, indirizzo_benzinaio, comune_benzinaio)) 
    
    #estraggo la latitudine e la longitudine e li mette in un vettore chiama punto
    latitudine_utente,longitudine_utente = estraiLatLong(dati_utente[5])        
    punto = (latitudine_utente, longitudine_utente)
    
    #Vedo quale benzinaio è entro il raggio desiderato
    benzinai_entro_raggio = benzinaioEntroRaggio(benzinai_dati, punto, float(dati_utente[4]))
    
    # Stampa i benzinaio entro il raggio
    for benzinaio in benzinai_entro_raggio:
        print(f"Benzinaio a {benzinaio[0]}, {benzinaio[1]} entro {dati_utente[4]} km." + " Prezzo: " + str(benzinaio[3]) + "€"+ " Indirizzo: " + str(benzinaio[4]) + " Comune: " + str(benzinaio[5]))
    
    return benzinai_entro_raggio

def InviaScelte(chat_id, options):
        url = f"{bot.api_url}sendMessage"
        keyboard = {
            "keyboard": [[{"text": option} for option in options]],
            "resize_keyboard": True, 
            "one_time_keyboard": True
        }
        payload = {
            "chat_id": chat_id,
            "text": "Seleziona un opzione",
            "reply_markup": json.dumps(keyboard)
        }
        requests.post(url, data=payload)

def getRisposta():
    global last_update_id
    
    while True:
        #sleep(5)
        data = bot.get_updates(last_update_id)
        if len(data['result']) > 0:
            last_update_id = data['result'][0]['update_id'] + 1
            return data

#Metodi per i calcoli

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Raggio della Terra in chilometri

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def benzinaioEntroRaggio(benzinai, punto, raggio):
    #Vettore dove sono tutti i benzinaio entro il raggio
    benzinaio_entro_raggio = []

    for benzinaio in benzinai:
        distanza = haversine(punto[0], punto[1], benzinaio[1], benzinaio[2])

        if distanza <= raggio:
            print(benzinaio[0], "è entro il raggio")
            benzinaio_entro_raggio.append(benzinaio)

    return benzinaio_entro_raggio

def estraiLatLong(coordinate_string):
    # Utilizza espressione regolare per estrarre latitudine e longitudine dalla stringa
    match = re.match(r"Longitudine:(?P<longitudine>[-+]?\d*\.\d+),\s*Latitudine:(?P<latitudine>[-+]?\d*\.\d+)", coordinate_string)
    
    if match:
        longitudine = float(match.group("longitudine"))
        latitudine = float(match.group("latitudine"))
        return latitudine, longitudine
    else:
        raise ValueError("Formato delle coordinate non valido")

#main
if __name__ == '__main__':
    main()