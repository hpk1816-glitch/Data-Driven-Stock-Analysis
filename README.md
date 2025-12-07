Data-Driven Stock Analysis
End-to-End Project Using Python, SQL, Streamlit and Power BI

This project analyzes Nifty 50 stock performance over one full year.
It includes data extraction, cleaning, transformation, visualization, sector analysis,
and dashboard building — all automated using Python and SQL.

Project Highlights

Data Sources
Input data provided in YAML format (month-wise folders)
Converted into structured CSV files
Combined into a master dataset and ticker-wise CSVs

Technologies Used
Python (Pandas, NumPy, Matplotlib)
MySQL
SQLAlchemy and mysql.connector
Streamlit
Power BI

Project Structure
Data-Driven Stock Analysis/
│
├── data/                     # Raw monthly stock data (YAML → CSV)
├── Ticker_CSVs/              # 50 stock-wise consolidated CSV files
├── monthly_charts/           # Visualization images
│
├── app.py                    # Streamlit dashboard
├── db_demo.py                # MySQL demo connection script
├── final_sql.sql             # Database schema and tables
│
├── master_dataset.csv        # Cleaned final dataset
├── master_cleaned.csv        # Processed dataset before final merge
│
├── market_summary.csv        # Market summary output
├── top_10_green.csv          # Top gainers
├── top_10_loss.csv           # Top losers
├── top_10_volatile.csv       # Most volatile stocks
│
├── correlation_matrix.csv    # Correlation output
│
├── preparation.py            # YAML to CSV preprocessing
├── combine_csvs_final.py     # Combine all files into master dataset
├── volatility_analysis.py    # Volatility calculations
├── cumulative_return_analysis.py # Cumulative returns
├── sector_performance.py     # Sector-wise analysis
│
└── README.md                 # Project documentation

How to Run the Project
1. Install Requirements
pip install pandas numpy matplotlib streamlit sqlalchemy mysql-connector-python

2. Set Up MySQL
Inside MySQL Workbench or terminal, run:
SOURCE final_sql.sql;

Make sure your MySQL credentials match:
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "stock_analysis"

3. Run the Streamlit Dashboard
streamlit run app.py
The dashboard will open at:
http://localhost:8501/

Power BI Dashboard
Includes:
Top gainers and losers
Sector performance
Monthly insights
Volatility comparison

Key Insights Delivered
Best and worst performing stocks
Month-wise and sector-wise performance
Market overview for the entire year
Correlation between stocks
Identification of high-volatility stocks

Contact
Created by: Prakash H
