import os

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

START_DATE = "2022-01-01"
