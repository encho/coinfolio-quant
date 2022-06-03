import pandas as pd
from cryptocmd import CmcScraper
import json
import yfinance as yf


cryptocurrencies_db = [
    {"ticker": "BTC-USD", "base": "BTC", "quote": "USD"},
    {"ticker": "ETH-USD", "base": "ETH", "quote": "USD"},
    {"ticker": "XRP-USD", "base": "XRP", "quote": "USD"},
]


print("helloooo")

# data = yf.download("EURUSD=X", start='2022-05-01')

df = yf.download("EURUSD=X", start='2022-05-01')

df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close",
                        "Date": "date", "Volume": "volume", "Adj Close": "adjusted_close"})

df.index.names = ['date']

print(df.head())

result = df.to_json(orient="table")

print(result)

# if __name__ == '__main__':
#     app.run()
