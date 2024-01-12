from telegram.ext import Application, CommandHandler, MessageHandler, filters

#VARIABILI
# Inizializza il token del bot
TOKEN = '6949498361:AAGdysoT7C9uMgWlwxlS-FcgSJwXKQwQeNw'

# Variabile per memorizzare il nome dell'utente
nome_utente = None
serbatoio_capienza = None
tipo_benzina = None
consuma_macchina = None
max_km = None

nome_utente_gia_salutato = False


# Definisci la funzione per il comando /start
async def start(update, context):
    await update.message.reply_text("Buon giornissimo ziaaa ☕ \r\nCome ti chiami?")

# Funzione che serve per rispondere
async def rispondi(update, context):
    global nome_utente, nome_utente_gia_salutato, serbatoio_capienza, tipo_benzina, consuma_macchina, max_km
    
    text = update.message.text.lower()
    
    #if per le varie informazioni
    
    #if per il nome
    if nome_utente is None:
        nome_utente = text
        await update.message.reply_text("Ciao " + nome_utente + "!")
    elif not nome_utente_gia_salutato:
        await update.message.reply_text("Ciao " + nome_utente + ", iniziamo col fare la benzina")
        await update.message.reply_text("Quanta benzina vuoi fare?")
        nome_utente_gia_salutato = True
        
    #if per la benzina
    if "litri" in text:
        await update.message.reply_text("Ok, " + nome_utente)
        await update.message.reply_text("Ok, " + nome_utente + " adesso dimmi la tipologia di benzina che vorresti fare")

    #if per la tipologia di benzina (tanti if per le varie tipologie)
    if "GPL"in text:
        tipo_benzina = text
        await update.message.reply_text("Ok, " + nome_utente)
        await update.message.reply_text("Ok, " + nome_utente + " dimmi quanti litri al km consuma la tua macchina")
        
    if "gasolio" in text:
        tipo_benzina = text
        await update.message.reply_text("Ok, " + nome_utente)
        await update.message.reply_text("Ok, " + nome_utente + " dimmi quanti litri al km consuma la tua macchina")
        
    if "benzina" in text:
        tipo_benzina = text
        await update.message.reply_text("Ok, " + nome_utente)
        await update.message.reply_text("Ok, " + nome_utente + " dimmi quanti litri al km consuma la tua macchina")
        
    #if per la capeinza del serbatooio
    if "km" in text:
        consuma_macchina = text
        await update.message.reply_text("Ok, " + nome_utente)
        await update.message.reply_text("Ok, " + nome_utente + " dimmi la capienza del tuo serbatoio")
        
    #if per la capeinza del serbatooio
    if "serbatoio" in text:
        serbatoio_capienza = text
        await update.message.reply_text("Ok, " + nome_utente)
        await update.message.reply_text("Ok, " + nome_utente + " adesso inviami la tua posizione")
    
# Definisci la funzione per la gestione della posizione
async def posizione(update, context):
    global attesa_posizione
    if update.message.location:
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
        await update.message.reply_text(f"Grazie per aver condiviso la tua posizione: "
                                        f"Latitudine: {latitude}, Longitudine: {longitude}")
    else:
        await update.message.reply_text("Per favore, invia una posizione.")




#MAIN
application = Application.builder().token(TOKEN).build()

# Aggiungi i gestori dei comandi
application.add_handler(CommandHandler('start', start))

# Aggiungi il gestore della posizione
application.add_handler(MessageHandler(filters.LOCATION, posizione))

# Aggiungi il gestore delle risposte ai messaggi
application.add_handler(MessageHandler(None, rispondi))



# Aggiungi il gestore delle risposte
application.run_polling(1.0)    # Run bot



#COSE DA FARE
#data pos
#trova il benzianio più vicino e conveniente
#75-90 litri