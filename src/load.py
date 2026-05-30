import logging
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_engine():
    server   = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DATABASE")
    username = os.getenv("AZURE_SQL_USERNAME")
    password = os.getenv("AZURE_SQL_PASSWORD")

    if not all([server, database, username, password]):
        raise EnvironmentError("One or more Azure SQL env vars are missing.")

    connection_url = (f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server")

    return create_engine(connection_url)


def _row_to_params(row: pd.Series) -> dict:
    """Convert a DataFrame row to SQL params; NaN → None for nullable floats."""
    params = {}
    for col, val in row.items():
        if pd.isna(val):
            params[col] = None
        elif hasattr(val, "item"):
            params[col] = val.item()
        else:
            params[col] = val
    params["chk_ticker"] = params["ticker"]
    params["chk_price_date"] = params["price_date"]
    return params


def insert_dataframe(df: pd.DataFrame, engine) -> int:
    """
    Insert rows into stock_prices, skipping any (ticker, price_date)
    combinations that already exist (idempotent load).
    Returns number of rows inserted.
    """
    cols = [
        "ticker", "sector", "price_date", "open_price", "high_price",
        "low_price", "close_price", "volume",
        "daily_return", "daily_range", "volatility_7d",
    ]
    df = df[cols].copy()
    df["price_date"] = df["price_date"].dt.strftime("%Y-%m-%d")

    inserted = 0
    stmt = text("""
        INSERT INTO stock_prices (
            ticker, sector, price_date, open_price, high_price,
            low_price, close_price, volume,
            daily_return, daily_range, volatility_7d
        )
        SELECT
            :ticker, :sector, :price_date, :open_price, :high_price,
            :low_price, :close_price, :volume,
            :daily_return, :daily_range, :volatility_7d
        WHERE NOT EXISTS (
            SELECT 1 FROM stock_prices
            WHERE ticker = :chk_ticker AND price_date = :chk_price_date
        )
    """)

    with engine.begin() as conn:
        for _, row in df.iterrows():
            result = conn.execute(stmt, _row_to_params(row))
            inserted += result.rowcount

        logger.info(f"Inserted {inserted} rows")
        return inserted

def run_load(df: pd.DataFrame) -> None:
    engine = get_engine()
    inserted = insert_dataframe(df, engine)
    logger.info(f"Loaded {inserted} rows")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Quick test run
    from transform import run_transformation
    df = run_transformation()
    if df is not None:
        run_load(df)