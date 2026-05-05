BOT AMAZON OFFERS - CREATORS API V4

File inclusi:
- main.py
- bot.py
- amazon_api.py
- settings.py
- category_keywords.py
- response_parser.py
- create_messages.py
- telegram_sender.py
- storage.py
- requirements.txt
- Procfile

ENV VARS RAILWAY:
- TELEGRAM_BOT_TOKEN=...
- TELEGRAM_CHAT_ID=...
- AMAZON_CLIENT_ID=amzn1.application-oa2-client....
- AMAZON_CLIENT_SECRET=amzn1.oa2-cs....
- AMAZON_PARTNER_TAG=capofferte-21
- AMAZON_MARKETPLACE=www.amazon.it
- AMAZON_REGION=eu
- AMAZON_TOKEN_URL=https://api.amazon.com/auth/o2/token
- AMAZON_API_BASE=DA PRENDERE DALLA DOC DELLA TUA APP CREATORS API
- AMAZON_SCOPE=DA PRENDERE DALLA DOC DELLA TUA APP CREATORS API
- CHECK_INTERVAL=1800
- MIN_PRICE=0
- MAX_PRICE=0
- MIN_DISCOUNT=0
- TOP_N=5

NOTE:
1) La Creators API usa OAuth 2.0 client credentials, non AWS SigV4.
2) Il token endpoint Login with Amazon e' https://api.amazon.com/auth/o2/token.
3) Devi ancora inserire AMAZON_API_BASE e, se richiesto, AMAZON_SCOPE esatti della tua app/documentazione.
4) Se il token risponde ma la search va in 404/401, bisogna correggere il path finale dell'endpoint usando la documentazione reale della tua app Creators API.
