import logging
import time
import requests

from settings import (
    AMAZON_CLIENT_ID,
    AMAZON_CLIENT_SECRET,
    AMAZON_PARTNER_TAG,
    AMAZON_MARKETPLACE,
    AMAZON_REGION,
    AMAZON_TOKEN_URL,
    AMAZON_API_BASE,
    AMAZON_SCOPE,
    MIN_PRICE,
    MAX_PRICE,
)
from response_parser import parse_items

logger = logging.getLogger(__name__)

_token_cache = {
    'access_token': None,
    'expires_at': 0,
}


def get_access_token() -> str:
    now = time.time()
    if _token_cache['access_token'] and now < _token_cache['expires_at'] - 60:
        return _token_cache['access_token']

    data = {
        'grant_type': 'client_credentials',
        'client_id': AMAZON_CLIENT_ID,
        'client_secret': AMAZON_CLIENT_SECRET,
    }
    if AMAZON_SCOPE:
        data['scope'] = AMAZON_SCOPE

    response = requests.post(
        AMAZON_TOKEN_URL,
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()

    access_token = payload['access_token']
    expires_in = int(payload.get('expires_in', 3600))
    _token_cache['access_token'] = access_token
    _token_cache['expires_at'] = now + expires_in
    return access_token


def search_items(keyword: str, search_index: str = 'All') -> list[dict]:
    token = get_access_token()

    payload = {
        'keywords': keyword,
        'partnerTag': AMAZON_PARTNER_TAG,
        'marketplace': AMAZON_MARKETPLACE,
        'searchIndex': search_index,
    }

    if MIN_PRICE > 0:
        payload['minPrice'] = MIN_PRICE
    if MAX_PRICE > 0:
        payload['maxPrice'] = MAX_PRICE

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Amz-Partner-Tag': AMAZON_PARTNER_TAG,
        'X-Amz-Marketplace': AMAZON_MARKETPLACE,
        'X-Amz-Region': AMAZON_REGION,
    }

    candidate_paths = [
        '/creators-api/searchitems',
        '/creators/searchitems',
        '/searchitems',
        '/v1/searchitems',
    ]

    last_error = None
    for path in candidate_paths:
        url = AMAZON_API_BASE.rstrip('/') + path
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 404:
                last_error = RuntimeError(f'404 on {url}')
                continue
            response.raise_for_status()
            return parse_items(response.json())
        except Exception as exc:
            logger.warning('Tentativo Creators API fallito su %s: %s', url, exc)
            last_error = exc

    raise RuntimeError(
        'Creators API request failed. Imposta AMAZON_API_BASE e AMAZON_SCOPE corretti dal pannello Amazon. '
        f'Ultimo errore: {last_error}'
    )
