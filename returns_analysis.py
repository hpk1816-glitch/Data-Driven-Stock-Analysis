"""
Returns Analysis Script

Calculates yearly returns per ticker and produces:
- top_10_green.csv
- top_10_loss.csv
"""

import pandas as pd

INPUT_FILE = "master_cleaned.csv"


def main() -> None:
    """Calculate yearly returns for each ticker."""
    df = pd.read_csv(INPUT_FILE)

    # Ensure date is datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Sort properly
    df = df.sort_values(["Ticker", "date"], kind="stable")

    # Compute first and last close price per ticker
    grouped = df.groupby("Ticker")

    first_close = grouped["close"].first()
    last_close = grouped["close"].last()

    yearly_return = (last_close - first_close) / first_close
    yearly_return = yearly_return.rename("yearly_return")

    # Put into one DataFrame
    result = yearly_return.reset_index()

    # Top 10 green
    top_green = result.sort_values("yearly_return", ascending=False).head(10)
    top_green.to_csv("top_10_green.csv", index=False)

    # Top 10 loss
    top_loss = result.sort_values("yearly_return", ascending=True).head(10)
    top_loss.to_csv("top_10_loss.csv", index=False)

    # Summary
    print("Returns analysis completed.")
    print("Saved: top_10_green.csv")
    print("Saved: top_10_loss.csv")


if __name__ == "__main__":
    main()
