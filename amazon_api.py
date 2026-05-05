import datetime as dt
import hashlib
import hmac
import json

import requests

from settings import (
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_PARTNER_TAG,
    AMAZON_MARKETPLACE,
    AMAZON_HOST,
    AMAZON_REGION,
    SEARCH_INDEX,
    MIN_PRICE_EUR,
    MAX_PRICE_EUR,
    MIN_SAVING_PERCENT,
    REQUEST_TIMEOUT,
    MAX_RESULTS_PER_KEYWORD,
)

PAAPI_TARGET = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems"
PAAPI_URI = "/paapi5/searchitems"
session = requests.Session()


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def get_signature_key(key, date_stamp, region_name, service_name):
    k_date = sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = hmac.new(k_date, region_name.encode("utf-8"), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service_name.encode("utf-8"), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()
    return k_signing


def eur_to_minor_units(value: float) -> int:
    return int(round(value * 100))


def build_headers(payload_json: str):
    now = dt.datetime.utcnow()
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    canonical_headers = (
        "content-encoding:amz-1.0\n"
        "content-type:application/json; charset=utf-8\n"
        f"host:{AMAZON_HOST}\n"
        f"x-amz-date:{amz_date}\n"
        f"x-amz-target:{PAAPI_TARGET}\n"
    )
    signed_headers = "content-encoding;content-type;host;x-amz-date;x-amz-target"

    canonical_request = "\n".join([
        "POST",
        PAAPI_URI,
        "",
        canonical_headers,
        signed_headers,
        payload_hash,
    ])

    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{date_stamp}/{AMAZON_REGION}/ProductAdvertisingAPI/aws4_request"
    string_to_sign = "\n".join([
        algorithm,
        amz_date,
        credential_scope,
        hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
    ])

    signing_key = get_signature_key(AMAZON_SECRET_KEY, date_stamp, AMAZON_REGION, "ProductAdvertisingAPI")
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    authorization_header = (
        f"{algorithm} Credential={AMAZON_ACCESS_KEY}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    return {
        "Content-Encoding": "amz-1.0",
        "Content-Type": "application/json; charset=utf-8",
        "Host": AMAZON_HOST,
        "X-Amz-Date": amz_date,
        "X-Amz-Target": PAAPI_TARGET,
        "Authorization": authorization_header,
    }


def search_items(keyword: str, search_index: str = SEARCH_INDEX) -> list:
    payload = {
        "Keywords": keyword,
        "SearchIndex": search_index,
        "ItemCount": MAX_RESULTS_PER_KEYWORD,
        "ItemPage": 1,
        "Marketplace": AMAZON_MARKETPLACE,
        "PartnerTag": AMAZON_PARTNER_TAG,
        "PartnerType": "Associates",
        "MinPrice": eur_to_minor_units(MIN_PRICE_EUR),
        "MaxPrice": eur_to_minor_units(MAX_PRICE_EUR),
        "MinSavingPercent": MIN_SAVING_PERCENT,
        "Resources": [
            "Images.Primary.Large",
            "ItemInfo.Title",
            "ItemInfo.Features",
            "Offers.Listings.Price",
            "Offers.Listings.SavingBasis",
            "Offers.Listings.Availability.Message",
            "Offers.Listings.Availability.Type",
            "Offers.Listings.MerchantInfo",
            "Offers.Listings.ProgramEligibility.IsPrimeExclusive",
            "Offers.Listings.DeliveryInfo.IsPrimeEligible"
        ]
    }

    payload_json = json.dumps(payload, separators=(",", ":"))
    headers = build_headers(payload_json)
    response = session.post(
        f"https://{AMAZON_HOST}{PAAPI_URI}",
        data=payload_json,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("Errors"):
        raise RuntimeError(str(data["Errors"]))

    return data.get("SearchResult", {}).get("Items", [])
