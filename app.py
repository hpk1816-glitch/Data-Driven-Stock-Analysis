# app.py
# Data-Driven Stock Analysis Dashboard

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


# -----------------------------
# Utility helpers
# -----------------------------
@st.cache_data
def load_csv(filename: str) -> pd.DataFrame | None:
    """Load a CSV from current folder, return None if missing or error."""
    if not os.path.exists(filename):
        return None
    try:
        return pd.read_csv(filename)
    except Exception:
        return None


def standardize_columns(df: pd.DataFrame, patterns: dict) -> pd.DataFrame | None:
    """
    Rename flexible column names to standard ones.

    patterns = {
        "Ticker": ["ticker", "symbol"],
        "yearly_return": ["yearly_return", "annual_return", "yearly_returns"],
        ...
    }
    """
    if df is None or df.empty:
        return None

    lower_map = {c.lower(): c for c in df.columns}
    rename = {}

    for target, candidates in patterns.items():
        found = None
        for cand in candidates:
            if cand.lower() in lower_map:
                found = lower_map[cand.lower()]
                break
        if found is None:
            # required column not present
            return None
        rename[found] = target

    return df.rename(columns=rename)


# -----------------------------
# Load specific datasets (robust)
# -----------------------------
@st.cache_data
def get_yearly_returns() -> pd.DataFrame | None:
    """
    Load yearly returns from stock_analysis_yearly_returns.csv
    or try to derive them from cumulative_full.csv.
    """
    # 1) Preferred pre-computed file
    candidates = [
        "stock_analysis_yearly_returns.csv",
        "yearly_returns.csv",
        "cumulative_return_analysis.csv",
    ]

    df = None
    for fn in candidates:
        df = load_csv(fn)
        if df is not None:
            df = standardize_columns(
                df,
                {
                    "Ticker": ["Ticker", "ticker", "symbol"],
                    "yearly_return": [
                        "yearly_return",
                        "annual_return",
                        "yearly_returns",
                        "total_return",
                    ],
                },
            )
            if df is not None:
                return df

    # 2) Fallback: derive from cumulative_full.csv
    cum = load_csv("cumulative_full.csv")
    if cum is None:
        return None

    cum = standardize_columns(
        cum,
        {
            "Ticker": ["Ticker", "ticker", "symbol"],
            "date": ["date"],
            "cumulative_return": ["cumulative_return", "cum_return"],
        },
    )
    if cum is None:
        return None

    # take last cumulative value per ticker as yearly return
    cum["date"] = pd.to_datetime(cum["date"])
    cum_sorted = cum.sort_values(["Ticker", "date"])
    last_vals = cum_sorted.groupby("Ticker")["cumulative_return"].last().reset_index()
    last_vals = last_vals.rename(columns={"cumulative_return": "yearly_return"})
    return last_vals


@st.cache_data
def get_volatility() -> pd.DataFrame | None:
    """Load volatility per stock from stock_analysis_volatility.csv or similar."""
    candidates = [
        "stock_analysis_volatility.csv",
        "volatility_analysis.csv",
        "stock_volatility.csv",
    ]
    df = None
    for fn in candidates:
        df = load_csv(fn)
        if df is not None:
            df = standardize_columns(
                df,
                {
                    "Ticker": ["Ticker", "ticker", "symbol"],
                    "volatility": ["volatility", "std_dev", "std"],
                },
            )
            if df is not None:
                return df
    return None


@st.cache_data
def get_sector_performance() -> pd.DataFrame | None:
    """Load sector performance if available."""
    candidates = [
        "sector_performance.csv",
        "sector_returns.csv",
    ]
    for fn in candidates:
        df = load_csv(fn)
        if df is not None:
            df = standardize_columns(
                df,
                {
                    "sector": ["sector", "Sector"],
                    "average_yearly_return": [
                        "average_yearly_return",
                        "avg_return",
                        "mean_return",
                    ],
                },
            )
            if df is not None:
                return df
    return None


@st.cache_data
def get_correlation_matrix() -> pd.DataFrame | None:
    """Load correlation matrix."""
    candidates = [
        "stock_analysis_correlation.csv",
        "correlation_matrix.csv",
    ]
    df = None
    for fn in candidates:
        df = load_csv(fn)
        if df is not None:
            # make sure first column is ticker/index
            # if needed, set index to first column when it's non-numeric
            if df.columns[0].lower() in ["ticker", "symbol"]:
                df = df.set_index(df.columns[0])
            # ensure it's numeric and square
            try:
                df = df.apply(pd.to_numeric, errors="coerce")
            except Exception:
                return None
            if df.shape[0] == df.shape[1]:
                return df
    return None


@st.cache_data
def get_master() -> pd.DataFrame | None:
    """Load master daily data."""
    master = load_csv("master_cleaned.csv")
    if master is None:
        master = load_csv("master_dataset.csv")

    if master is None:
        return None

    # standardize important columns
    patterns = {
        "date": ["date"],
        "Ticker": ["Ticker", "ticker", "symbol"],
        "open": ["open"],
        "high": ["high"],
        "low": ["low"],
        "close": ["close", "Close"],
        "volume": ["volume", "Volume"],
    }
    master = standardize_columns(master, patterns)
    if master is None:
        return None

    master["date"] = pd.to_datetime(master["date"])
    return master


@st.cache_data
def get_cumulative_full() -> pd.DataFrame | None:
    """Load cumulative returns time-series."""
    cum = load_csv("cumulative_full.csv")
    if cum is None:
        return None

    cum = standardize_columns(
        cum,
        {
            "date": ["date"],
            "Ticker": ["Ticker", "ticker", "symbol"],
            "daily_return": ["daily_return"],
            "cumulative_return": ["cumulative_return", "cum_return"],
        },
    )
    if cum is None:
        return None

    cum["date"] = pd.to_datetime(cum["date"])
    return cum


# -----------------------------
# Page implementations
# -----------------------------
def page_market_summary():
    st.header("Market Summary")

    yr = get_yearly_returns()
    if yr is None:
        st.info(
            "Could not find yearly returns data.\n\n"
            "Please keep a CSV like stock_analysis_yearly_returns.csv in this "
            "folder with columns Ticker and yearly_return."
        )
        return

    # basic metrics
    total_stocks = yr["Ticker"].nunique()
    green = (yr["yearly_return"] > 0).sum()
    red = (yr["yearly_return"] <= 0).sum()

    master = get_master()
    avg_price = master["close"].mean() if master is not None else np.nan
    avg_volume = master["volume"].mean() if master is not None else np.nan

    cols = st.columns(4)
    cols[0].metric("Total Stocks", int(total_stocks))
    cols[1].metric("Green Stocks", int(green))
    cols[2].metric("Red Stocks", int(red))
    cols[3].metric(
        "Average Price",
        f"{avg_price:.2f}" if not np.isnan(avg_price) else "NA",
    )

    st.write("")
    st.subheader("Annual Return of All Stocks (Heat-style Bar Chart)")

    yr_sorted = yr.sort_values("yearly_return", ascending=False)
    fig = px.bar(
        yr_sorted,
        x="Ticker",
        y="yearly_return",
        color="yearly_return",
        color_continuous_scale="Greens",
    )
    fig.update_layout(xaxis_title="Ticker", yaxis_title="Yearly Return")
    st.plotly_chart(fig, use_container_width=True)


def page_top_performing():
    st.header("Top Performing Stocks")

    yr = get_yearly_returns()
    if yr is None:
        st.info(
            "Could not find yearly returns with columns 'Ticker' "
            "and 'yearly_return'."
        )
        return

    top_n = st.slider("Select number of stocks", 5, 20, 10)
    top_green = yr.sort_values("yearly_return", ascending=False).head(top_n)

    fig = px.bar(
        top_green,
        x="Ticker",
        y="yearly_return",
        text="yearly_return",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        xaxis_title="Ticker",
        yaxis_title="Yearly Return",
        yaxis=dict(tickformat=".2f"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_green.reset_index(drop=True))


def page_least_performing():
    st.header("Least Performing Stocks")

    yr = get_yearly_returns()
    if yr is None:
        st.info(
            "Could not find yearly returns with columns 'Ticker' "
            "and 'yearly_return'."
        )
        return

    top_n = st.slider("Select number of stocks", 5, 20, 10)
    worst = yr.sort_values("yearly_return", ascending=True).head(top_n)

    fig = px.bar(
        worst,
        x="Ticker",
        y="yearly_return",
        text="yearly_return",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        xaxis_title="Ticker",
        yaxis_title="Yearly Return",
        yaxis=dict(tickformat=".2f"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(worst.reset_index(drop=True))


def page_daily_returns():
    st.header("Daily Returns & Cumulative Performance")

    cum = get_cumulative_full()
    if cum is None:
        st.info(
            "Need cumulative_full.csv with columns "
            "'Ticker', 'date', 'daily_return', 'cumulative_return'."
        )
        return

    tickers = sorted(cum["Ticker"].unique())
    selected = st.multiselect("Select stocks", tickers, default=tickers[:5])

    if not selected:
        st.warning("Please select at least one stock.")
        return

    filtered = cum[cum["Ticker"].isin(selected)].copy()

    st.subheader("Cumulative Returns Over Time")
    fig = px.line(
        filtered,
        x="date",
        y="cumulative_return",
        color="Ticker",
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Cumulative Return")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Daily Returns Distribution")
    fig2 = px.box(
        filtered,
        x="Ticker",
        y="daily_return",
    )
    fig2.update_layout(xaxis_title="Ticker", yaxis_title="Daily Return")
    st.plotly_chart(fig2, use_container_width=True)


def page_volatile():
    st.header("Volatile Stocks")

    vol = get_volatility()
    if vol is None:
        st.info(
            "Need stock_analysis_volatility.csv with columns "
            "'Ticker' and 'volatility'."
        )
        return

    top_n = st.slider("Select number of most volatile stocks", 5, 30, 10)
    vol_sorted = vol.sort_values("volatility", ascending=False).head(top_n)

    fig = px.bar(
        vol_sorted,
        x="Ticker",
        y="volatility",
        text="volatility",
    )
    fig.update_traces(texttemplate="%{text:.4f}", textposition="outside")
    fig.update_layout(
        xaxis_title="Ticker",
        yaxis_title="Volatility (Std Dev of Daily Returns)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(vol_sorted.reset_index(drop=True))


def page_sector_performance():
    st.header("Sector Performance")

    sec = get_sector_performance()
    if sec is None:
        st.info(
            "Need sector CSV with 'sector' and 'average_yearly_return'.\n\n"
            "Example: sector_performance.csv in the same folder."
        )
        return

    sec_sorted = sec.sort_values("average_yearly_return", ascending=False)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            sec_sorted,
            x="sector",
            y="average_yearly_return",
        )
        fig.update_layout(
            xaxis_title="Sector",
            yaxis_title="Average Yearly Return",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Sector Table")
        st.dataframe(sec_sorted.reset_index(drop=True))


def page_correlation():
    st.header("Stock Price Correlation")

    corr = load_csv("stock_analysis_correlation.csv")
    if corr is None or corr.empty:
        st.info("Need stock_analysis_correlation.csv (correlation matrix).")
        return

    # Keep a copy for table (with 'ticker' as a normal column)
    corr_table = corr.copy()

    # For the heatmap we need ticker as index and a square matrix
    if "ticker" in corr.columns:
        corr_matrix = corr.set_index("ticker")
    elif "Ticker" in corr.columns:
        corr_matrix = corr.set_index("Ticker")
    else:
        # assume first column is ticker
        corr_matrix = corr.set_index(corr.columns[0])

    st.subheader("Correlation of Stock Daily Returns ↩")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        corr_matrix,
        cmap="RdBu_r",
        center=0,
        cbar_kws={"label": "Correlation"},
        ax=ax,
    )
    ax.set_xlabel("Ticker")
    ax.set_ylabel("Ticker")
    st.pyplot(fig)

    # NEW: correlation table
    st.subheader("Correlation Table")
    # nicely rounded numbers
    st.dataframe(corr_table.round(3))



def page_price_trend():
    st.header("Stock Daily Price Trend")

    # Load master file safely (no "or" on DataFrames)
    master = load_csv("master_cleaned.csv")
    if master is None or master.empty:
        master = load_csv("master_dataset.csv")

    if master is None or master.empty:
        st.info("Need master_cleaned.csv or master_dataset.csv.")
        return

    # Make sure column names are in the correct form
    # (your file already uses these, this is just a safety check)
    cols = {c.lower(): c for c in master.columns}
    date_col = cols.get("date", "date")
    ticker_col = cols.get("ticker", "Ticker")
    close_col = cols.get("close", "close")

    # Convert date
    master[date_col] = pd.to_datetime(master[date_col])

    # --- Controls ---
    tickers = sorted(master[ticker_col].unique())
    default_tickers = tickers[:2] if len(tickers) >= 2 else tickers

    selected_tickers = st.multiselect(
        "Select Stock(s)",
        options=tickers,
        default=default_tickers,
    )

    if not selected_tickers:
        st.warning("Please select at least one stock.")
        return

    min_date = master[date_col].min().date()
    max_date = master[date_col].max().date()

    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
        )
    with c2:
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
        )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data
    mask = (
        master[ticker_col].isin(selected_tickers)
        & (master[date_col] >= start_date)
        & (master[date_col] <= end_date)
    )
    filtered = master.loc[mask].sort_values(date_col)

    if filtered.empty:
        st.warning("No data available for the selected options.")
        return

    # --- Line chart (same as before) ---
    fig = px.line(
        filtered,
        x=date_col,
        y=close_col,
        color=ticker_col,
        labels={date_col: "Date", close_col: "Close Price", ticker_col: "Ticker"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # NEW: price table under the chart
    st.subheader("Price Data Table")
    table = (
        filtered[[date_col, ticker_col, close_col]]
        .sort_values([ticker_col, date_col])
        .rename(
            columns={
                date_col: "Date",
                ticker_col: "Ticker",
                close_col: "Close Price",
            }
        )
    )
    st.dataframe(table)


# -----------------------------
# Main layout
# -----------------------------
def main():
    st.set_page_config(
        page_title="Data-Driven Stock Analysis",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.sidebar.title("Stock Analysis")
    st.sidebar.write("Navigation")

    page = st.sidebar.radio(
        "",
        [
            "Market Summary",
            "Top Performing Stocks",
            "Least Performing Stocks",
            "Daily Returns & Cumulative",
            "Volatile Stocks",
            "Sector Performance",
            "Stock Price Correlation",
            "Stock Daily Price Trend",
        ],
    )

    if page == "Market Summary":
        page_market_summary()
    elif page == "Top Performing Stocks":
        page_top_performing()
    elif page == "Least Performing Stocks":
        page_least_performing()
    elif page == "Daily Returns & Cumulative":
        page_daily_returns()
    elif page == "Volatile Stocks":
        page_volatile()
    elif page == "Sector Performance":
        page_sector_performance()
    elif page == "Stock Price Correlation":
        page_correlation()
    elif page == "Stock Daily Price Trend":
        page_price_trend()


if __name__ == "__main__":
    main()
