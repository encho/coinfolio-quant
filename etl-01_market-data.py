import os
import datetime
from pymongo import MongoClient
# import etl_load_crypto_ohlc_series
import yfinance as yf
import pandas as pd
import progressbar
import datetime


from etl_config import MARKET_DATA_METADATA


# def parse_date(date_string):
#     return datetime.datetime.strptime(date_string, "%Y-%m-%d")


# def get_dates_for_period(start_date_string, end_date_string):
#     start_date = parse_date(start_date_string)
#     dates = [start_date]
#     current_date = start_date

#     end_date = parse_date(end_date_string)

#     while current_date < end_date:
#         next_day = current_date + datetime.timedelta(days=1)
#         dates.append(next_day)
#         current_date = next_day
#     return dates


# TODO pass dates directly, not dates strings!
def fetch_and_store_series(market_data_series_collection, market_data_spec, start_date, end_date):

    # trick the yahoo api which would start one day before the passed date
    start_date = start_date + datetime.timedelta(days=1)

    # trick the yahoo api which will exclude the end date
    end_date = end_date + datetime.timedelta(days=1)

    ticker = market_data_spec["ticker"]
    yahoo_ticker = market_data_spec["yahoo_ticker"]

    print("starting to load: " + market_data_spec["ticker"])

    # download series data
    df = yf.download(yahoo_ticker, start=start_date, end=end_date)

    # rename columns
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close",
                            "Volume": "volume", "Adj Close": "adjusted_close"})
    df.index.names = ['date']

    df["percentage_change"] = (df['close'] /
                               df['close'].shift(1) - 1).fillna(0)

    df["adjusted_percentage_change"] = (df["adjusted_close"] /
                                        df["adjusted_close"].shift(1) - 1).fillna(0)

    total_rows = len(df)
    current_row = 0

    bar = progressbar.ProgressBar(maxval=total_rows, widgets=[
        progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

    bar.start()

    print(df)

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
            "percentage_change": row.percentage_change,
            "adjusted_percentage_change": row.adjusted_percentage_change,
        }
        market_data_series_collection.insert_one(record)

        current_row = current_row + 1
        bar.update(current_row)

    bar.finish()


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

CLIENT = MongoClient(MONGO_CONNECTION_STRING)
DATABASE = CLIENT["coinfolio_prod"]

START_DATE = datetime.date(2014, 9, 17)
END_DATE = datetime.date.today() - datetime.timedelta(days=1)

# --------------------------------------------------------------------
# STORE MARKET DATA METADATA INFO
# --------------------------------------------------------------------
# clean the DATABASE collection
market_data_metadata_collection = DATABASE["market_data_metadata"]
market_data_metadata_collection.drop()

for market_data_record in MARKET_DATA_METADATA:
    market_data_metadata_collection.insert_one(market_data_record)

# --------------------------------------------------------------------
# STORE MARKET DATA QUOTES
# --------------------------------------------------------------------
# clean the DATABASE collection
market_data_series_collection = DATABASE["market_data_series"]
market_data_series_collection.drop()
# insert the quotes
for market_data_spec in MARKET_DATA_METADATA:
    fetch_and_store_series(
        market_data_series_collection, market_data_spec, START_DATE, END_DATE)


CLIENT.close()
