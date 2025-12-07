"""
yaml_to_csv.py

Read all YAML files from the `data` folder (and subfolders) and create
one CSV per ticker in the `Ticker_CSVs` folder.

Each output file will have columns:
date, open, high, low, close, volume, Ticker
"""

from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List

import pandas as pd
import yaml

YAML_ROOT_FOLDER = "data"
OUTPUT_FOLDER = "Ticker_CSVs"


def load_yaml(path: str) -> Any:
    """Load and return parsed YAML, or None on error."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except Exception as exc:
        print(f"⚠️  Failed to read/parse {path}: {exc}")
        return None


def iter_records(parsed: Any) -> Iterable[Dict[str, Any]]:
    """
    Yield individual records from the parsed YAML.

    Handles these shapes:
    1) A list of records
    2) A dict with key 'daily' -> list of records
    3) A single dict that itself is a record with 'Ticker'
    4) A dict whose values are records or lists of records with 'Ticker'
    """
    # Case 1: list of records
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict):
                yield item
        return

    # Case 2–4: dict-based
    if not isinstance(parsed, dict):
        return

    # Case 2: dict with 'daily'
    daily = parsed.get("daily")
    if isinstance(daily, list):
        for item in daily:
            if isinstance(item, dict):
                yield item
        return

    # Case 3: dict itself is a record
    if "Ticker" in parsed or "ticker" in parsed:
        yield parsed
        return

    # Case 4: nested dicts/lists that contain records
    for value in parsed.values():
        if isinstance(value, dict):
            if "Ticker" in value or "ticker" in value:
                yield value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and (
                    "Ticker" in item or "ticker" in item
                ):
                    yield item


def ensure_row(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert one YAML record into a row with fixed keys:
    date, open, high, low, close, volume, Ticker
    """
    ticker = record.get("Ticker") or record.get("ticker")

    return {
        "date": record.get("date"),
        "open": record.get("open"),
        "high": record.get("high"),
        "low": record.get("low"),
        "close": record.get("close"),
        "volume": record.get("volume"),
        "Ticker": ticker,
    }


def main() -> None:
    """Main routine: read YAML and write one CSV per ticker."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # key: ticker, value: list of row dicts
    stocks_data: Dict[str, List[Dict[str, Any]]] = {}

    if not os.path.isdir(YAML_ROOT_FOLDER):
        print(f"❌ YAML root folder not found: {YAML_ROOT_FOLDER}")
        return

    # Walk through data/ and all subfolders
    for root, _dirs, files in os.walk(YAML_ROOT_FOLDER):
        for file_name in files:
            if not file_name.endswith(".yaml"):
                continue

            file_path = os.path.join(root, file_name)
            parsed = load_yaml(file_path)
            if parsed is None:
                continue

            for raw in iter_records(parsed):
                ticker = raw.get("Ticker") or raw.get("ticker")
                if not ticker:
                    continue

                row = ensure_row(raw)

                # Skip records that have no prices at all
                if (
                    row["open"] is None
                    and row["high"] is None
                    and row["low"] is None
                    and row["close"] is None
                ):
                    continue

                stocks_data.setdefault(ticker, []).append(row)

    if not stocks_data:
        print("⚠️  No data found in YAML files.")
        return

    # Write one CSV per ticker
    for ticker, rows in stocks_data.items():
        df = pd.DataFrame(rows)

        # Sort by date if possible
        try:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.sort_values("date", kind="stable")
        except Exception:
            pass

        # Ensure column order
        cols = ["date", "open", "high", "low", "close", "volume", "Ticker"]
        df = df[cols]

        out_path = os.path.join(OUTPUT_FOLDER, f"{ticker}.csv")
        df.to_csv(out_path, index=False)

    print("✅ Done! One CSV per ticker created in 'Ticker_CSVs'.")


if __name__ == "__main__":
    main()
