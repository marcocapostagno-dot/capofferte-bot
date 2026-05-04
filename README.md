# Amazon Telegram Bot

Bot semplice per pubblicare offerte Amazon su Telegram con link affiliato.

## Funzioni
- Selezione keyword con punteggio
- Costruzione link Amazon con tag affiliato
- Invio automatico a uno o più canali Telegram
- Logging base per debug su Railway

## Variabili ambiente
- BOT_TOKEN=token del bot Telegram
- AFFILIATE_TAG=tuo tag Amazon, es. capofferte-21
- CHANNELS=@Capofferte,@AltroCanale
- POST_INTERVAL_SECONDS=10800
- REQUEST_TIMEOUT=20

## Avvio locale
```bash
pip install -r requirements.txt
python main.py
```

## Deploy su Railway
1. Carica questi file su GitHub
2. Vai su Railway
3. Crea un nuovo progetto con **Deploy from GitHub repo**
4. Seleziona il repository
5. Aggiungi le variabili ambiente
6. Avvia il deploy

## Note
- Il bot deve essere admin del canale Telegram per poter pubblicare messaggi.
- Questa versione pubblica contenuti basati su keyword, non ancora prodotti live presi da API Amazon.
- Il testo include disclosure affiliata.
