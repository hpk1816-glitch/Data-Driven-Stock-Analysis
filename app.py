import os
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


# -------------------------------------------------
# Helper: load CSV with basic cleaning
# -------------------------------------------------
@st.cache_data
def load_csv(path):
    df = pd.read_csv(path)
    # standardise column names to lower case
    df.columns = [c.strip().lower() for c in df.columns]
    return df


# -------------------------------------------------
# Check that all required CSV files exist
# -------------------------------------------------
DATA_FILES = {
    "market_summary": "market_summary.csv",
    "top_10_green": "top_10_green.csv",
    "top_10_loss": "top_10_loss.csv",
    "top_10_volatile": "top_10_volatile.csv",
    "sector_performance": "sector_performance.csv",
    "correlation_matrix": "correlation_matrix.csv",
    "cumulative_full": "cumulative_full.csv",
    "monthly_top_5_gainers": "monthly_top_5_gainers.csv",
    "monthly_top_5_losers": "monthly_top_5_losers.csv",
}


def check_files_exist():
    missing = []
    for key, fname in DATA_FILES.items():
        if not os.path.exists(fname):
            missing.append(fname)
    return missing


missing_files = check_files_exist()

if missing_files:
    st.error(
        "One or more CSV files are missing. "
        "Please check that these files are in the same folder as app.py:\n\n"
        + "\n".join(f"- {f}" for f in missing_files)
    )
    st.stop()


# -------------------------------------------------
# Load all datasets
# -------------------------------------------------
market_summary_df = load_csv(DATA_FILES["market_summary"])
top_10_green_df = load_csv(DATA_FILES["top_10_green"])
top_10_loss_df = load_csv(DATA_FILES["top_10_loss"])
top_10_vol_df = load_csv(DATA_FILES["top_10_volatile"])
sector_perf_df = load_csv(DATA_FILES["sector_performance"])
corr_matrix_df = load_csv(DATA_FILES["correlation_matrix"])
cumulative_full_df = load_csv(DATA_FILES["cumulative_full"])
monthly_gainers_df = load_csv(DATA_FILES["monthly_top_5_gainers"])
monthly_losers_df = load_csv(DATA_FILES["monthly_top_5_losers"])

# Some CSVs may have "ticker" or "symbol" or "stock" etc.
# Normalise to "ticker" where possible.
for df in [
    top_10_green_df,
    top_10_loss_df,
    top_10_vol_df,
    cumulative_full_df,
    monthly_gainers_df,
    monthly_losers_df,
]:
    if "ticker" not in df.columns:
        if "symbol" in df.columns:
            df.rename(columns={"symbol": "ticker"}, inplace=True)
        elif "stock" in df.columns:
            df.rename(columns={"stock": "ticker"}, inplace=True)
        elif "ticker " in df.columns:
            df.rename(columns={"ticker ": "ticker"}, inplace=True)


# -------------------------------------------------
# Page 1: Overview
# -------------------------------------------------
def page_overview():
    st.title("Data-Driven Stock Analysis Dashboard")
    st.subheader("Project Overview")

    st.write(
        """
This dashboard summarises Nifty 50 stock performance for the last year.

You can view:
- Top 10 gainers and losers
- Volatility of each stock
- Sector wise performance
- Correlation between stock prices
- Cumulative returns over time
- Monthly top 5 gainers and losers
        """
    )

    st.subheader("Market Summary")
    st.dataframe(market_summary_df)

    # Try to show some key metrics if columns exist
    cols = list(market_summary_df["metric"])
    metrics = dict(zip(market_summary_df["metric"], market_summary_df["value"]))

    col1, col2, col3, col4 = st.columns(4)
    if "green_stocks" in metrics:
        col1.metric("Green stocks", int(metrics["green_stocks"]))
    if "red_stocks" in metrics:
        col2.metric("Red stocks", int(metrics["red_stocks"]))
    if "average_price" in metrics:
        col3.metric("Average close price", round(float(metrics["average_price"]), 2))
    if "average_volume" in metrics:
        col4.metric("Average volume", int(metrics["average_volume"]))


# -------------------------------------------------
# Page 2: Top 10 gainers and losers
# -------------------------------------------------
def page_top_10():
    st.title("Top 10 Gainers and Losers")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 gainers")
        st.dataframe(top_10_green_df)

        if "ticker" in top_10_green_df.columns and "yearly_return" in top_10_green_df.columns:
            fig, ax = plt.subplots()
            ax.bar(top_10_green_df["ticker"], top_10_green_df["yearly_return"])
            ax.set_xlabel("Ticker")
            ax.set_ylabel("Yearly return")
            ax.set_xticklabels(top_10_green_df["ticker"], rotation=45, ha="right")
            st.pyplot(fig)

    with col2:
        st.subheader("Top 10 losers")
        st.dataframe(top_10_loss_df)

        if "ticker" in top_10_loss_df.columns and "yearly_return" in top_10_loss_df.columns:
            fig, ax = plt.subplots()
            ax.bar(top_10_loss_df["ticker"], top_10_loss_df["yearly_return"], color="red")
            ax.set_xlabel("Ticker")
            ax.set_ylabel("Yearly return")
            ax.set_xticklabels(top_10_loss_df["ticker"], rotation=45, ha="right")
            st.pyplot(fig)


# -------------------------------------------------
# Page 3: Volatility (Top 10)
# -------------------------------------------------
def page_volatility():
    st.title("Volatility (Top 10)")

    st.subheader("Top 10 most volatile stocks")
    st.dataframe(top_10_vol_df)

    if "ticker" in top_10_vol_df.columns and "volatility" in top_10_vol_df.columns:
        fig, ax = plt.subplots()
        ax.bar(top_10_vol_df["ticker"], top_10_vol_df["volatility"])
        ax.set_xlabel("Ticker")
        ax.set_ylabel("Volatility (standard deviation of daily returns)")
        ax.set_xticklabels(top_10_vol_df["ticker"], rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.info("Columns 'ticker' and 'volatility' are required in top_10_volatile.csv.")


# -------------------------------------------------
# Page 4: Sector performance
# -------------------------------------------------
def page_sector_performance():
    st.title("Sector performance")

    st.subheader("Average yearly return by sector")
    st.dataframe(sector_perf_df)

    if "sector" in sector_perf_df.columns and "average_yearly_return" in sector_perf_df.columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(sector_perf_df["sector"], sector_perf_df["average_yearly_return"])
        ax.set_xlabel("Sector")
        ax.set_ylabel("Average yearly return")
        ax.set_xticklabels(sector_perf_df["sector"], rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.info(
            "Columns 'sector' and 'average_yearly_return' are required in sector_performance.csv."
        )


# -------------------------------------------------
# Page 5: Price correlation heatmap
# -------------------------------------------------
def page_correlation_heatmap():
    st.title("Price correlation heatmap")

    st.subheader("Correlation matrix table")
    st.dataframe(corr_matrix_df)

    st.subheader("Stock price correlation heatmap")

    # assume first column is ticker and rest are correlation values
    if corr_matrix_df.shape[1] > 1:
        corr_only = corr_matrix_df.iloc[:, 1:]
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_only, cmap="Reds", ax=ax)
        st.pyplot(fig)
    else:
        st.info("correlation_matrix.csv should contain one column for ticker and others for correlation values.")


# -------------------------------------------------
# Page 6: Cumulative returns over time
# -------------------------------------------------
def page_cumulative_returns():
    st.title("Cumulative returns over time")

    st.subheader("Sample of raw data")
    st.dataframe(cumulative_full_df.head())

    required_cols = {"ticker", "date", "cumulative_return"}
    if not required_cols.issubset(cumulative_full_df.columns):
        st.info(
            "cumulative_full.csv needs columns: 'ticker', 'date', 'cumulative_return'.\n"
            "Currently it has: " + ", ".join(cumulative_full_df.columns)
        )
        return

    # Convert date
    cumulative_full_df["date"] = pd.to_datetime(cumulative_full_df["date"])

    tickers = sorted(cumulative_full_df["ticker"].unique())
    default_selection = tickers[:5]

    selected = st.multiselect(
        "Select tickers to plot", options=tickers, default=default_selection
    )

    if not selected:
        st.info("Please select at least one ticker.")
        return

    fig, ax = plt.subplots(figsize=(8, 4))
    for t in selected:
        temp = cumulative_full_df[cumulative_full_df["ticker"] == t]
        ax.plot(temp["date"], temp["cumulative_return"], label=t)

    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative return")
    ax.legend()
    st.pyplot(fig)


# -------------------------------------------------
# Page 7: Monthly top 5 gainers and losers
# -------------------------------------------------
def page_monthly_top5():
    st.title("Monthly top 5 gainers and losers")

    required_cols = {"ticker", "month", "monthly_return", "rank"}
    if not required_cols.issubset(monthly_gainers_df.columns) or not required_cols.issubset(
        monthly_losers_df.columns
    ):
        st.info(
            "monthly_top_5_gainers.csv and monthly_top_5_losers.csv "
            "must have columns: 'ticker', 'month', 'monthly_return', 'rank'."
        )
        return

    months = sorted(monthly_gainers_df["month"].unique())
    selected_month = st.selectbox("Select month", options=months)

    g_df = monthly_gainers_df[monthly_gainers_df["month"] == selected_month]
    l_df = monthly_losers_df[monthly_losers_df["month"] == selected_month]

    st.subheader(f"Month: {selected_month}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("Top 5 gainers")
        st.dataframe(g_df)

    with col2:
        st.markdown("Top 5 losers")
        st.dataframe(l_df)


# -------------------------------------------------
# Page 8: Raw data explorer
# -------------------------------------------------
def page_raw_data():
    st.title("Raw data explorer")

    options = {
        "Market summary": market_summary_df,
        "Top 10 green": top_10_green_df,
        "Top 10 loss": top_10_loss_df,
        "Top 10 volatile": top_10_vol_df,
        "Sector performance": sector_perf_df,
        "Correlation matrix": corr_matrix_df,
        "Cumulative full": cumulative_full_df,
        "Monthly top 5 gainers": monthly_gainers_df,
        "Monthly top 5 losers": monthly_losers_df,
    }

    choice = st.selectbox("Select dataset", list(options.keys()))
    st.write("Showing data from:", choice)
    st.dataframe(options[choice])


# -------------------------------------------------
# Main layout
# -------------------------------------------------
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        (
            "Overview",
            "Top 10 gainers and losers",
            "Volatility (Top 10)",
            "Sector performance",
            "Price correlation heatmap",
            "Cumulative returns",
            "Monthly top 5 gainers and losers",
            "Raw data explorer",
        ),
    )

    if page == "Overview":
        page_overview()
    elif page == "Top 10 gainers and losers":
        page_top_10()
    elif page == "Volatility (Top 10)":
        page_volatility()
    elif page == "Sector performance":
        page_sector_performance()
    elif page == "Price correlation heatmap":
        page_correlation_heatmap()
    elif page == "Cumulative returns":
        page_cumulative_returns()
    elif page == "Monthly top 5 gainers and losers":
        page_monthly_top5()
    elif page == "Raw data explorer":
        page_raw_data()


if __name__ == "__main__":
    main()
