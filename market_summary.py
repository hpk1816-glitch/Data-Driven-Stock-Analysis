"""
Market Summary Script

Calculates:
- Number of green vs. red stocks
- Average close price across all stocks
- Average volume across all stocks
Outputs:
market_summary.csv
"""

import pandas as pd

INPUT_FILE = "master_cleaned.csv"


def main() -> None:
    """Compute market summary metrics."""
    df = pd.read_csv(INPUT_FILE)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Sort to ensure proper yearly return calculation
    df = df.sort_values(["Ticker", "date"], kind="stable")

    grouped = df.groupby("Ticker")

    first_close = grouped["close"].first()
    last_close = grouped["close"].last()

    yearly_return = (last_close - first_close) / first_close
    yearly_return = yearly_return.rename("yearly_return")

    result = yearly_return.reset_index()

    green_count = (result["yearly_return"] > 0).sum()
    red_count = (result["yearly_return"] < 0).sum()

    avg_price = df["close"].mean()
    avg_volume = df["volume"].mean()

    summary = pd.DataFrame({
        "metric": ["green_stocks", "red_stocks", "average_price", "average_volume"],
        "value": [green_count, red_count, avg_price, avg_volume]
    })

    summary.to_csv("market_summary.csv", index=False)

    print("Market summary completed.")
    print("Saved as: market_summary.csv")
    print(f"Green stocks: {green_count}")
    print(f"Red stocks: {red_count}")
    print(f"Average price: {avg_price}")
    print(f"Average volume: {avg_volume}")


if __name__ == "__main__":
    main()
