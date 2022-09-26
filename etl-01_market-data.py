import os
import datetime
from pymongo import MongoClient
import etl_load_crypto_ohlc_series

from etl_config import MARKET_DATA_METADATA


def parse_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%d")


def get_dates_for_period(start_date_string, end_date_string):
    start_date = parse_date(start_date_string)
    dates = [start_date]
    current_date = start_date

    end_date = parse_date(end_date_string)

    while current_date < end_date:
        next_day = current_date + datetime.timedelta(days=1)
        dates.append(next_day)
        current_date = next_day
    return dates


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


# TODO have this as datetime object, yahoo fetching function needs to transform this into string eventually
# long backtest
START_DATE = "2014-09-17"  # not there for eth
END_DATE = "2022-09-26"

# short backtest
# START_DATE = "2020-01-02"
# END_DATE = "2020-12-31"

# START_DATE = "2021-08-16"  # not there for eth
# END_DATE = "2022-08-16"

# --------------------------------------------------------------------
# STORE MARKET DATA METADATA INFO
# --------------------------------------------------------------------
# clean the database collection
market_data_metadata_collection = database["market_data_metadata"]
market_data_metadata_collection.drop()

for market_data_record in MARKET_DATA_METADATA:
    market_data_metadata_collection.insert_one(market_data_record)

# --------------------------------------------------------------------
# CRYPTOCURRENCY QUOTES
# --------------------------------------------------------------------
# clean the database collection
cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
cryptocurrency_quotes_collection.drop()
# insert the quotes
for cryptocurrency in MARKET_DATA_METADATA:
    etl_load_crypto_ohlc_series.run(
        cryptocurrency_quotes_collection, cryptocurrency, START_DATE, END_DATE)


client.close()
