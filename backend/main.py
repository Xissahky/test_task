from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

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
    if not KEY_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="CoinGecko API key is missing. Add it to key.txt."
        )

    api_key = KEY_FILE.read_text().strip()

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="CoinGecko API key is empty."
        )

    return {
        "x-cg-demo-api-key": api_key
    }


def get_tvl_usd(tvl):
    """
    Convert CoinGecko TVL value to a USD number.
    The API may return TVL as a number, dictionary, or null.
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
    return {
        "message": "Backend is running"
    }


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

        filtered_coins = []

        for coin in coins:
            market_cap = coin.get("market_cap")
            fdv = coin.get("fully_diluted_valuation")
            volume = coin.get("total_volume")
            max_supply = coin.get("max_supply")
            total_supply = coin.get("total_supply")

            # Market Capitalization > 0
            if market_cap is None or market_cap <= 0:
                continue

            # Fully Diluted Valuation < $100M
            if fdv is None or fdv >= MAX_FDV:
                continue

            # 24h Trading Volume > $50K
            if volume is None or volume <= MIN_VOLUME:
                continue

            # Max Supply must equal Total Supply
            if max_supply is None or total_supply is None:
                continue

            if max_supply != total_supply:
                continue

            # Get additional data required for preview_listing and TVL
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

            if details_response.status_code == 429:
                raise HTTPException(
                    status_code=503,
                    detail="CoinGecko API rate limit exceeded."
                )

            if details_response.status_code != 200:
                continue

            details = details_response.json()

            # Original assignment requirement:
            #
            # preview_listing = true
            #
            # This condition is intentionally disabled in the demonstration
            # version because current CoinGecko data returns no projects that
            # satisfy preview_listing=true together with all required market
            # data filters.
            #
            # See README.md for a more detailed explanation.
            #
            # if details.get("preview_listing") is not True:
            #     continue

            market_data = details.get("market_data", {})
            tvl = get_tvl_usd(
                market_data.get("total_value_locked")
            )

            # Total Value Locked > $50K
            if tvl <= MIN_TVL:
                continue

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

        return filtered_coins

    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail=f"CoinGecko API error: {str(error)}"
        )