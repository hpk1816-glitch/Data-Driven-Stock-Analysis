"""
Cumulative Return Analysis Script

Calculates cumulative returns for each stock across the full
date range. Outputs:
- top_5_cumulative.csv (tickers with highest final return)
- cumulative_full.csv (full time-series for line charts)
"""

import pandas as pd

INPUT_FILE = "master_cleaned.csv"


def main() -> None:
    """Compute cumulative returns for each ticker."""
    df = pd.read_csv(INPUT_FILE)

    # Ensure proper types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["daily_return"] = pd.to_numeric(df["daily_return"], errors="coerce")

    # Clean rows
    df = df.dropna(subset=["daily_return"])

    # Sort
    df = df.sort_values(["Ticker", "date"], kind="stable")

    # Compute cumulative return for each ticker
    df["cumulative_return"] = (
        (1 + df["daily_return"]).groupby(df["Ticker"]).cumprod() - 1
    )

    # Save the full dataset for charts
    df.to_csv("cumulative_full.csv", index=False)

    # Extract final cumulative return per ticker
    last_values = df.groupby("Ticker")["cumulative_return"].last()
    last_values = last_values.rename("final_cumulative_return")

    # Get top 5 performing stocks
    top_5 = last_values.sort_values(ascending=False).head(5)
    top_5.to_csv("top_5_cumulative.csv")

    print("Cumulative return analysis completed.")
    print("Saved: top_5_cumulative.csv and cumulative_full.csv")
    print("Top 5 performing stocks based on cumulative return:")
    print(top_5)


if __name__ == "__main__":
    main()
