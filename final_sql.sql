CREATE DATABASE IF NOT EXISTS stock_analysis;
USE stock_analysis;
USE stock_analysis;
CREATE TABLE stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    ticker VARCHAR(20)
);
SELECT COUNT(*) FROM stocks;
CREATE OR REPLACE VIEW yearly_returns AS
SELECT 
    ticker,
    ( (MAX(close) - MIN(close)) / MIN(close) ) AS yearly_return
FROM stocks
GROUP BY ticker;
CREATE OR REPLACE VIEW daily_returns AS
SELECT 
    id,
    date,
    ticker,
    close,
    (close - LAG(close) OVER (PARTITION BY ticker ORDER BY date)) 
        / LAG(close) OVER (PARTITION BY ticker ORDER BY date) AS daily_return
FROM stocks;
CREATE OR REPLACE VIEW volatility AS
SELECT 
    ticker,
    STDDEV(daily_return) AS volatility
FROM daily_returns
GROUP BY ticker;
CREATE OR REPLACE VIEW monthly_returns AS
SELECT 
    ticker,
    DATE_FORMAT(date, '%Y-%m') AS month,
    ( (MAX(close) - MIN(close)) / MIN(close) ) AS monthly_return
FROM stocks
GROUP BY ticker, month;

