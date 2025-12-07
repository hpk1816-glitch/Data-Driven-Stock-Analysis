"""
Preparation Script

This script loads the master dataset, cleans the data,
sorts by ticker and date, converts numeric values, and
calculates daily returns. Output: master_cleaned.csv
"""

import pandas as pd

MASTER_FILE = "master_dataset.csv"


def main() -> None:
    """Main function to clean and prepare stock data."""

    # Load dataset
    df = pd.read_csv(MASTER_FILE)

    # Strip spaces from column names (safety)
    df.columns = [col.strip() for col in df.columns]

    # Check required columns
    required_cols = ["date", "open", "high", "low", "close", "volume", "Ticker"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    # Convert date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Convert numeric columns
    numeric_columns = ["open", "high", "low", "close", "volume"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with no Ticker or no close price
    df = df.dropna(subset=["Ticker", "close"])

    # Sort by Ticker and date
    df = df.sort_values(["Ticker", "date"], kind="stable")

    # Set MultiIndex: Ticker + date
    df = df.set_index(["Ticker", "date"])

    # Forward fill within each ticker (grouped by index level 0)
    df = df.groupby(level=0).ffill()

    # Calculate daily returns per ticker (still using index level 0)
    df["daily_return"] = df.groupby(level=0)["close"].pct_change()

    # Bring Ticker and date back as normal columns
    df = df.reset_index()

    # Save cleaned data
    df.to_csv("master_cleaned.csv", index=False)

    print("Preparation completed successfully.")
    print("Saved cleaned dataset as: master_cleaned.csv")


if __name__ == "__main__":
    main()
