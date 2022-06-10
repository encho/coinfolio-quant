import os
from pymongo import MongoClient
from etl import load_crypto_ohlc_series

# from ..cryptocurrencies import get_cryptocurrency_dataframe
from datalake.cryptocurrencies import get_cryptocurrency_dataframe

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

START_DATE = "2022-06-01"

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

STRATEGIES = [
    {"ticker": "G4_EQUALLY_WEIGHTED",
     "name": "Equally Weighted G4 Basket",
        "description": "Equally weighted portfolio of 4 main cryptocurrencies."},
    {"ticker": "G2_EQUALLY_WEIGHTED",
     "name": "Equally Weighted G2 Basket",
        "description": "Equally weighted portfolio of 2 main cryptocurrencies."},
]


# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]
cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
cryptocurrency_quotes_collection.drop()

strategies_collection = database["strategies"]
strategies_collection.drop()

# insert all strategies into database
for strategy in STRATEGIES:
    strategies_collection.insert_one(strategy)

# insert all enriched cryptocurrency ohlc quotes into database
for cryptocurrency in CRYPTOCURRENCIES:
    load_crypto_ohlc_series.run(
        cryptocurrency_quotes_collection, cryptocurrency, START_DATE)

# TODO: create the history of equal weighted G4/5 strategy!

# TODO: create first backtest with equal weighted strategy

client.close()
