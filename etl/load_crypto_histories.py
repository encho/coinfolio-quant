import yfinance as yf
from pymongo import MongoClient
import os
import progressbar


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]
cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
cryptocurrency_quotes_collection.drop()

cryptocurrencies_db = [
    {"ticker": "BTC-USD", "base": "BTC", "quote": "USD"},
    {"ticker": "ETH-USD", "base": "ETH", "quote": "USD"},
    {"ticker": "XRP-USD", "base": "XRP", "quote": "USD"},
    {"ticker": "ADA-USD", "base": "ADA", "quote": "USD"},
    {"ticker": "BTC-EUR", "base": "BTC", "quote": "EUR"},
    {"ticker": "ETH-EUR", "base": "ETH", "quote": "EUR"},
    {"ticker": "XRP-EUR", "base": "XRP", "quote": "EUR"},
    {"ticker": "ADA-EUR", "base": "ADA", "quote": "EUR"},
]

start_date = "2020-01-01"

print("loading cryptocurrency quotes...")
print("================================")
for cryptocurrency in cryptocurrencies_db:
    ticker = cryptocurrency["ticker"]
    base = cryptocurrency["base"]
    quote = cryptocurrency["quote"]

    print("starting to load: " + cryptocurrency["ticker"])

    df = yf.download(ticker, start=start_date)
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close",
                            "Volume": "volume", "Adj Close": "adjusted_close"})
    df.index.names = ['date']

    print(df.head())

    records = df.to_records()

    total_rows = len(df)
    current_row = 0

    bar = progressbar.ProgressBar(maxval=total_rows, widgets=[
                                  progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

    bar.start()

    for index, row in df.iterrows():

        record = {
            "ticker": ticker,
            "date": index,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
            "adjusted_close": row.adjusted_close,
        }
        cryptocurrency_quotes_collection.insert_one(record)

        current_row = current_row + 1
        bar.update(current_row)

    bar.finish()
