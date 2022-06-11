import os
import datetime
from pymongo import MongoClient
from etl import load_crypto_ohlc_series
from etl.load_strategy_weights import create_strategy_weights


def get_dates_until_today(date_string):
    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    dates = [date]
    current_date = date

    today_at_midnight = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)

    while current_date < today_at_midnight:
        next_day = current_date + datetime.timedelta(days=1)
        dates.append(next_day)
        current_date = next_day
    return dates


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
    {
        "ticker": "G4_EQUALLY_WEIGHTED",
        "name": "Equally Weighted G4 Basket",
        "description": "Equally weighted portfolio of 4 main cryptocurrencies.",
    },
    {
        "ticker": "G2_EQUALLY_WEIGHTED",
        "name": "Equally Weighted G2 Basket",
        "description": "Equally weighted portfolio of 2 main cryptocurrencies.",
    }
]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


# insert all strategies into database
# --------------------------------------------------------------------
# clean the database collection
strategies_collection = database["strategies"]
strategies_collection.drop()
# insert the strategies infos
for strategy in STRATEGIES:
    strategies_collection.insert_one(strategy)

# insert all enriched cryptocurrency ohlc quotes into database
# --------------------------------------------------------------------
# clean the database collection
cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
cryptocurrency_quotes_collection.drop()
# insert the quotes
for cryptocurrency in CRYPTOCURRENCIES:
    load_crypto_ohlc_series.run(
        cryptocurrency_quotes_collection, cryptocurrency, START_DATE)


# insert all enriched cryptocurrency ohlc quotes into database
# --------------------------------------------------------------------
# clean the database collection
strategies_weights_collection = database["strategies_weights"]
strategies_weights_collection.drop()
# create the history of equal weighted G4/5 strategy!
dates_until_today = get_dates_until_today(START_DATE)

for strategy in STRATEGIES:
    for date in dates_until_today:
        create_strategy_weights(strategies_weights_collection,
                                strategy["ticker"], date)


client.close()
