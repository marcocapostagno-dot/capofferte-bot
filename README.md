# Amazon Telegram Bot V3

Struttura ispirata al modello Piero24, adattata per Railway e per i tuoi parametri:
- Amazon.it
- autopost automatico
- più keyword in lista
- migliori N prodotti per ciclo
- filtro prezzo minimo / massimo
- filtro sconto minimo
- storage SQLite per evitare doppi ASIN

## Struttura progetto
- `main.py` entrypoint
- `bot.py` loop principale e logica pubblicazione
- `settings.py` configurazione via env vars
- `category_keywords.py` categorie e keyword
- `amazon_api.py` chiamata PA-API SearchItems
- `response_parser.py` parser e scoring dei prodotti
- `telegram_sender.py` invio a Telegram
- `create_messages.py` testo del messaggio
- `storage.py` SQLite per ASIN già inviati

## Variabili ambiente richieste
- `BOT_TOKEN`
- `CHANNELS=@Capofferte`
- `AMAZON_ACCESS_KEY`
- `AMAZON_SECRET_KEY`
- `AMAZON_PARTNER_TAG`
- `AMAZON_MARKETPLACE=www.amazon.it`
- `AMAZON_HOST=webservices.amazon.it`
- `AMAZON_REGION=eu-west-1`
- `SEARCH_INDEX=All`
- `KEYWORDS=smartphone,cuffie gaming,smartwatch,powerbank,tablet,monitor gaming`
- `MIN_PRICE_EUR=20`
- `MAX_PRICE_EUR=300`
- `MIN_SAVING_PERCENT=15`
- `MAX_ITEMS_PER_CYCLE=3`
- `MAX_RESULTS_PER_KEYWORD=10`
- `POST_INTERVAL_SECONDS=10800`
- `PAUSE_BETWEEN_MESSAGES_SECONDS=2`
- `REQUEST_TIMEOUT=30`
- `ONLY_AMAZON=false`
- `ONLY_PRIME=false`
- `DB_PATH=bot_data.sqlite3`

## Deploy su Railway
1. Carica i file su GitHub
2. Collega il repo a Railway
3. Inserisci le variabili ambiente
4. Deploya il servizio worker

## Note
- La PA-API accetta una keyword per richiesta, quindi il bot itera su più keyword e poi ordina i risultati.
- `MinPrice` e `MaxPrice` vengono convertiti in centesimi, come richiesto dalla documentazione PA-API.
- Il bot salva gli ASIN inviati in SQLite per non ripubblicare gli stessi prodotti.
