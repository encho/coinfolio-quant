import os
from pymongo import MongoClient
from etl import load_crypto_ohlc_series

# from ..cryptocurrencies import get_cryptocurrency_dataframe
from datalake.cryptocurrencies import get_cryptocurrency_dataframe

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

CRYPTOCURRENCIES = [
    {"ticker": "BTC-USD", "base": "BTC", "quote": "USD"},
    {"ticker": "ETH-USD", "base": "ETH", "quote": "USD"},
    {"ticker": "XRP-USD", "base": "XRP", "quote": "USD"},
    {"ticker": "ADA-USD", "base": "ADA", "quote": "USD"},
    # {"ticker": "BTC-EUR", "base": "BTC", "quote": "EUR"},
    # {"ticker": "ETH-EUR", "base": "ETH", "quote": "EUR"},
    # {"ticker": "XRP-EUR", "base": "XRP", "quote": "EUR"},
    # {"ticker": "ADA-EUR", "base": "ADA", "quote": "EUR"},
]

START_DATE = "2020-01-01"

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]
cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
cryptocurrency_quotes_collection.drop()

for cryptocurrency in CRYPTOCURRENCIES:
    load_crypto_ohlc_series.run(
        cryptocurrency_quotes_collection, cryptocurrency, START_DATE)

# TODO: create the history of equal weighted G4/5 strategy!

# TODO: create first backtest with equal weighted strategy

client.close()
