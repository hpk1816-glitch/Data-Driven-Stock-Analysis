"""
Monthly Performance Analysis

This script calculates:
- Monthly returns for each stock
- Top 5 gainers per month
- Top 5 losers per month

Outputs:
- monthly_top_5_gainers.csv
- monthly_top_5_losers.csv
- charts saved in folder 'monthly_charts/'
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


INPUT_FILE = "master_cleaned.csv"
GAINERS_FILE = "monthly_top_5_gainers.csv"
LOSERS_FILE = "monthly_top_5_losers.csv"
CHART_DIR = "monthly_charts"


def ensure_output_folder() -> None:
    """Create folder for charts if not exists."""
    os.makedirs(CHART_DIR, exist_ok=True)


def calculate_monthly_return(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly returns grouped by ticker."""
    df["month"] = df["date"].dt.to_period("M").astype(str)

    monthly = (
        df.groupby(["Ticker", "month"])["close"]
        .agg(["first", "last"])
        .reset_index()
    )

    monthly["monthly_return"] = (
        (monthly["last"] - monthly["first"]) / monthly["first"]
    )

    return monthly.dropna(subset=["monthly_return"])


def save_top_performers(monthly: pd.DataFrame) -> None:
    """Save top 5 gainers and losers for each month."""
    gainers_list = []
    losers_list = []

    for month in monthly["month"].unique():
        month_data = monthly[monthly["month"] == month]

        top5 = month_data.nlargest(5, "monthly_return")
        bottom5 = month_data.nsmallest(5, "monthly_return")

        top5["rank"] = range(1, len(top5) + 1)
        bottom5["rank"] = range(1, len(bottom5) + 1)

        gainers_list.append(top5)
        losers_list.append(bottom5)

    pd.concat(gainers_list).to_csv(GAINERS_FILE, index=False)
    pd.concat(losers_list).to_csv(LOSERS_FILE, index=False)

    print(f"Saved: {GAINERS_FILE}")
    print(f"Saved: {LOSERS_FILE}")


def plot_monthly_charts(monthly: pd.DataFrame) -> None:
    """Generate bar charts for top gainers and losers per month."""
    for month in monthly["month"].unique():
        month_data = monthly[monthly["month"] == month]

        top5 = month_data.nlargest(5, "monthly_return")
        bottom5 = month_data.nsmallest(5, "monthly_return")

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(top5["Ticker"], top5["monthly_return"], color="green")
        ax.set_title(f"Top 5 Gainers - {month}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{CHART_DIR}/gainers_{month}.png")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(bottom5["Ticker"], bottom5["monthly_return"], color="red")
        ax.set_title(f"Top 5 Losers - {month}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{CHART_DIR}/losers_{month}.png")
        plt.close(fig)


def main() -> None:
    """Main execution workflow."""
    df = pd.read_csv(INPUT_FILE)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    ensure_output_folder()

    monthly = calculate_monthly_return(df)
    save_top_performers(monthly)
    plot_monthly_charts(monthly)

    print("\nMonthly performance analysis completed.")
    print(f"Charts saved inside '{CHART_DIR}/'")


if __name__ == "__main__":
    main()
