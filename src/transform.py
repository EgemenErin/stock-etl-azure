# src/transform.py

import json
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = REPO_ROOT / "data" / "raw"

TICKERS = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL":  "Technology",
    "NVDA":  "Technology",
    "JNJ":  "Healthcare",
}

def load_raw_json(ticker: str) -> dict | None:
    """Load the most recent raw JSON file for a given ticker."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filepath = RAW_DATA_DIR / ticker / f"{today}.json"

    if not filepath.exists():
        logger.warning(f"{ticker} → No raw file found at {filepath}")
        return None

    with open(filepath, "r") as f:
        return json.load(f)


def parse_time_series(ticker: str, raw: dict) -> pd.DataFrame | None:
    """
    Parse the Alpha Vantage TIME_SERIES_DAILY response
    into a clean, typed DataFrame.
    """
    time_series = raw.get("Time Series (Daily)")
    if not time_series:
        logger.error(f"{ticker} → 'Time Series (Daily)' key missing from raw data")
        return None

    rows = []
    for date_str, values in time_series.items():
        rows.append({
            "ticker":      ticker,
            "sector":      TICKERS[ticker],
            "price_date":  date_str,
            "open_price":  float(values["1. open"]),
            "high_price":  float(values["2. high"]),
            "low_price":   float(values["3. low"]),
            "close_price": float(values["4. close"]),
            "volume":      int(values["5. volume"]),
        })

    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df = df.sort_values("price_date").reset_index(drop=True)

    logger.info(f"{ticker} → Parsed {len(df)} rows")
    return df


def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate volatility and return metrics per ticker.

    - daily_return : % change in close price vs previous trading day
    - daily_range  : high - low (intraday volatility proxy)
    - volatility_7d: rolling 7-day std of daily returns (annualised)
    """
    df = df.copy()

    df["daily_return"] = df["close_price"].pct_change().round(6)

    df["daily_range"] = (df["high_price"] - df["low_price"]).round(4)

    # Rolling 7-day std of returns — multiply by sqrt(252) to annualise
    df["volatility_7d"] = (
        df["daily_return"]
        .rolling(window=7, min_periods=7)
        .std()
        .mul((252 ** 0.5))
        .round(6)
    )

    logger.info(f"Metrics added: daily_return, daily_range, volatility_7d")
    return df


def run_transformation() -> pd.DataFrame | None:
    all_frames = []

    for ticker in TICKERS:
        raw = load_raw_json(ticker)
        if raw is None:
            continue

        df = parse_time_series(ticker, raw)
        if df is None:
            continue

        df = add_metrics(df)
        all_frames.append(df)

    if not all_frames:
        logger.error("No data transformed — all tickers failed.")
        return None

    combined = pd.concat(all_frames, ignore_index=True)
    logger.info(f"Transformation complete. Total rows: {len(combined)}")
    return combined


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    df = run_transformation()
    if df is not None:
        print(df.tail(10).to_string())