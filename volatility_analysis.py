"""
Volatility Analysis Script

Calculates volatility for each stock based on the standard
deviation of daily returns and outputs the top 10 most volatile
stocks as top_10_volatile.csv.
"""

import pandas as pd

INPUT_FILE = "master_cleaned.csv"


def main() -> None:
    """Compute volatility for each stock."""
    df = pd.read_csv(INPUT_FILE)

    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Ensure numerical columns are numeric
    df["daily_return"] = pd.to_numeric(df["daily_return"], errors="coerce")

    # Drop rows without daily returns
    df = df.dropna(subset=["daily_return"])

    # Group by ticker and calculate volatility
    volatility = df.groupby("Ticker")["daily_return"].std()
    volatility = volatility.rename("volatility")

    # Get top 10 most volatile
    top_10 = volatility.sort_values(ascending=False).head(10)
    top_10.to_csv("top_10_volatile.csv")

    print("Volatility analysis completed.")
    print("Saved as: top_10_volatile.csv")
    print("Top 10 most volatile stocks:")
    print(top_10)


if __name__ == "__main__":
    main()
