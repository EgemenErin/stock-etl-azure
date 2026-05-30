import requests
from datetime import datetime, timedelta, timezone
import json
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = REPO_ROOT / "data" / "raw"

TICKERS = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL":  "Technology",
    "NVDA":  "Technology",
    "JNJ":  "Healthcare",
}

REQUEST_DELAY_SECONDS = 13

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

def fetch_daily_data(ticker: str) -> dict:
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "compact",
        "apikey": API_KEY,
    }
    logger.info(f"Fetching daily data for {ticker}")
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            logger.error(f"{ticker} → API error: {data['Error Message']}")
            return None

        if "Note" in data:
            logger.warning(f"{ticker} → Rate limit hit: {data['Note']}")
            return None

        if "Information" in data:
            logger.warning(f"{ticker} → API message: {data['Information']}")
            return None

        logger.info(f"{ticker} → OK ({len(data.get('Time Series (Daily)', {}))} rows)")
        return data

    except requests.exceptions.Timeout:
        logger.error(f"{ticker} → Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"{ticker} → Request failed: {e}")
        return None

def save_raw(ticker: str, data: dict) -> Path:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ticker_dir = RAW_DATA_DIR / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)

    filepath = ticker_dir / f"{today}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"{ticker} → Saved raw to {filepath}")
    return filepath

def run_extraction() -> dict[str, Path]:
    if not API_KEY:
        raise EnvironmentError("ALPHA_VANTAGE_API_KEY not found in environment.")

    results = {}

    for i, (ticker, sector) in enumerate(TICKERS.items()):
        data = fetch_daily_data(ticker)

        if data:
            path = save_raw(ticker, data)
            results[ticker] = path
        else:
            logger.warning(f"{ticker} → Skipped (no data returned)")

        # Rate limit pause — skip after last ticker
        if i < len(TICKERS) - 1:
            logger.info(f"Waiting {REQUEST_DELAY_SECONDS}s (rate limit)...")
            time.sleep(REQUEST_DELAY_SECONDS)

    logger.info(f"Extraction complete. {len(results)}/{len(TICKERS)} tickers saved.")
    return results

if __name__ == "__main__":
    results = run_extraction()
    print(results)
