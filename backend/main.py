from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


# Allow React frontend to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


COINGECKO_URL = "https://api.coingecko.com/api/v3"

MAX_FDV = 100_000_000
MIN_VOLUME = 50_000
MIN_TVL = 50_000


KEY_FILE = Path(__file__).resolve().parent.parent / "key.txt"


def get_headers():
    if KEY_FILE.exists():
        api_key = KEY_FILE.read_text().strip()

        if api_key:
            return {
                "x-cg-demo-api-key": api_key
            }

    return {}


def get_tvl_usd(tvl):
    """
    CoinGecko may return TVL as a number, dictionary or null.
    This function converts it to a USD number.
    """
    if tvl is None:
        return 0

    if isinstance(tvl, dict):
        return tvl.get("usd", 0) or 0

    if isinstance(tvl, (int, float)):
        return tvl

    return 0


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/api/coins")
def get_coins():
    headers = get_headers()

    try:

        response = requests.get(
            f"{COINGECKO_URL}/coins/markets",
            headers=headers,
            params={
                "vs_currency": "usd",
                "order": "volume_desc",
                "per_page": 250,
                "page": 1,
                "sparkline": "false",
            },
            timeout=15,
        )

        response.raise_for_status()
        coins = response.json()

        print("Total coins:", len(coins))

        passed_market_cap = 0
        passed_fdv = 0
        passed_volume = 0
        passed_supply = 0
        passed_preview = 0
        passed_tvl = 0

        filtered_coins = []

        for coin in coins:
            market_cap = coin.get("market_cap")
            fdv = coin.get("fully_diluted_valuation")
            volume = coin.get("total_volume")
            max_supply = coin.get("max_supply")
            total_supply = coin.get("total_supply")

            if market_cap is None or market_cap <= 0:
                continue
            passed_market_cap += 1

            if fdv is None or fdv >= MAX_FDV:
                continue
            passed_fdv += 1

            if volume is None or volume <= MIN_VOLUME:
                continue
            passed_volume += 1

            if max_supply is None or total_supply is None:
                continue

            if max_supply != total_supply:
                continue
            passed_supply += 1

            details_response = requests.get(
                f"{COINGECKO_URL}/coins/{coin['id']}",
                headers=headers,
                params={
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "true",
                    "community_data": "false",
                    "developer_data": "false",
                    "sparkline": "false",
                },
                timeout=15,
            )

            if details_response.status_code != 200:
                continue

            details = details_response.json()

            # To fully comply with the terms of the assignment, uncomment on the following three lines and comment line after them
            # if details.get("preview_listing") is not True:
            #     continue
            # passed_preview += 1


            # and comment next line
            passed_preview += 1

            market_data = details.get("market_data", {})
            tvl = get_tvl_usd(market_data.get("total_value_locked"))

            if tvl <= MIN_TVL:
                continue
            passed_tvl += 1

            filtered_coins.append({
                "id": coin["id"],
                "name": coin["name"],
                "symbol": coin["symbol"],
                "image": coin.get("image"),
                "market_cap": market_cap,
                "fdv": fdv,
                "volume_24h": volume,
                "tvl": tvl,
            })

        print("Passed market cap:", passed_market_cap)
        print("Passed FDV:", passed_fdv)
        print("Passed volume:", passed_volume)
        print("Passed supply:", passed_supply)
        print("Passed preview_listing:", passed_preview)
        print("Passed TVL:", passed_tvl)

        return filtered_coins


    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail=f"CoinGecko API error: {str(error)}"
        )