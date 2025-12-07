"""
Sector Performance Analysis

- Reads master_cleaned.csv for price data
- Reads Sector_data - Sheet1.csv for sector mapping
- Computes yearly return per ticker
- Calculates average yearly return per sector
- Outputs: sector_performance.csv
"""

import pandas as pd

MASTER_FILE = "master_cleaned.csv"
SECTOR_FILE = "Sector_data - Sheet1.csv"


def detect_columns(df: pd.DataFrame) -> tuple[str, str]:
    """
    Try to detect ticker and sector column names in a sector dataframe.
    Returns (ticker_col, sector_col).
    """
    lower_cols = {c.lower(): c for c in df.columns}

    # Candidate ticker column names
    ticker_candidates = [
        "ticker",
        "symbol",
        "stock",
        "stock_symbol",
        "company",
        "name",
    ]

    # Candidate sector column names
    sector_candidates = [
        "sector",
        "industry",
        "sector_name",
        "industry_name",
    ]

    ticker_col = None
    sector_col = None

    for key, orig in lower_cols.items():
        for t in ticker_candidates:
            if t in key:
                ticker_col = orig
                break
        if ticker_col is not None:
            break

    for key, orig in lower_cols.items():
        for s in sector_candidates:
            if s in key:
                sector_col = orig
                break
        if sector_col is not None:
            break

    if ticker_col is None or sector_col is None:
        raise ValueError(
            f"Could not detect ticker/sector columns. Columns found: {list(df.columns)}"
        )

    return ticker_col, sector_col


def main() -> None:
    """Compute average yearly return by sector."""
    # Load price data
    prices = pd.read_csv(MASTER_FILE)
    prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
    prices = prices.sort_values(["Ticker", "date"], kind="stable")

    # Yearly return per ticker
    grouped = prices.groupby("Ticker")
    first_close = grouped["close"].first()
    last_close = grouped["close"].last()

    yearly_return = (last_close - first_close) / first_close
    yearly_return = yearly_return.rename("yearly_return")
    returns = yearly_return.reset_index()

    # Load sector data
    sectors = pd.read_csv(SECTOR_FILE)
    sectors.columns = [c.strip() for c in sectors.columns]

    ticker_col, sector_col = detect_columns(sectors)

    # Normalise ticker names to match
    sectors[ticker_col] = sectors[ticker_col].astype(str).str.strip()
    returns["Ticker"] = returns["Ticker"].astype(str).str.strip()

    # Merge on ticker
    merged = returns.merge(
        sectors[[ticker_col, sector_col]],
        left_on="Ticker",
        right_on=ticker_col,
        how="left",
    )

    # Drop rows with no sector info
    merged = merged.dropna(subset=[sector_col])

    # Average yearly return per sector
    sector_perf = (
        merged.groupby(sector_col)["yearly_return"]
        .mean()
        .reset_index()
        .rename(columns={"yearly_return": "average_yearly_return"})
        .sort_values("average_yearly_return", ascending=False)
    )

    sector_perf.to_csv("sector_performance.csv", index=False)

    print("Sector performance analysis completed.")
    print("Saved as: sector_performance.csv")
    print(sector_perf)


if __name__ == "__main__":
    main()
