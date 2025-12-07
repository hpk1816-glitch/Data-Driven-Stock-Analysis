"""
Correlation Analysis Script

Calculates the correlation between stocks based on their
daily returns and outputs:
- correlation_matrix.csv
- correlation_heatmap.png
"""

import pandas as pd
import matplotlib.pyplot as plt


INPUT_FILE = "master_cleaned.csv"
MATRIX_FILE = "correlation_matrix.csv"
HEATMAP_FILE = "correlation_heatmap.png"


def main() -> None:
    """Compute correlation matrix and save heatmap."""
    # Load cleaned data
    df = pd.read_csv(INPUT_FILE)

    # Ensure correct types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["daily_return"] = pd.to_numeric(df["daily_return"], errors="coerce")

    # Drop rows without daily returns
    df = df.dropna(subset=["daily_return"])

    # Pivot: rows = date, columns = Ticker, values = daily_return
    pivot = df.pivot_table(
        index="date",
        columns="Ticker",
        values="daily_return"
    )

    # Compute correlation matrix
    corr_matrix = pivot.corr()

    # Save to CSV
    corr_matrix.to_csv(MATRIX_FILE)

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr_matrix, aspect="auto")

    # Ticks and labels
    tick_positions = range(len(corr_matrix.columns))
    ax.set_xticks(tick_positions)
    ax.set_yticks(tick_positions)
    ax.set_xticklabels(corr_matrix.columns, rotation=90)
    ax.set_yticklabels(corr_matrix.columns)

    # Color bar
    plt.colorbar(im, ax=ax)

    plt.tight_layout()
    plt.savefig(HEATMAP_FILE, dpi=300)
    plt.close(fig)

    print("Correlation analysis completed.")
    print(f"Saved matrix as: {MATRIX_FILE}")
    print(f"Saved heatmap as: {HEATMAP_FILE}")


if __name__ == "__main__":
    main()
