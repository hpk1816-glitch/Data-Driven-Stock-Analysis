"""
combine_csvs_final.py

Combine all ticker-wise CSVs from the Ticker_CSVs folder
into one master CSV: master_dataset.csv

Columns:
date, open, high, low, close, volume, Ticker
"""

import os
import glob
import pandas as pd

CSV_FOLDER = "Ticker_CSVs"
OUTPUT_FILE = "master_dataset.csv"


def main() -> None:
    csv_files = sorted(glob.glob(os.path.join(CSV_FOLDER, "*.csv")))
    
    if not csv_files:
        print("❌ No CSV files found in Ticker_CSVs.")
        return
    
    frames = []
    
    for file in csv_files:
        df = pd.read_csv(file)
        
        # Ensure correct column names
        df.columns = [c.strip() for c in df.columns]
        
        # Parse date
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            
        frames.append(df)
    
    # Combine all
    master = pd.concat(frames, ignore_index=True)
    
    # Remove duplicates
    before = len(master)
    master = master.drop_duplicates().reset_index(drop=True)
    removed = before - len(master)
    
    # Sort by Ticker + date
    master = master.sort_values(["Ticker", "date"], kind="stable")
    
    # Save
    master.to_csv(OUTPUT_FILE, index=False)
    
    print("✅ Master dataset created: master_dataset.csv")
    print(f"   Total rows: {len(master):,}")
    print(f"   Duplicate rows removed: {removed:,}")
    print(f"   Unique tickers: {master['Ticker'].nunique()}")


if __name__ == "__main__":
    main()
