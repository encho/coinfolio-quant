import os
import datetime
from pymongo import MongoClient
import datetime

# from etl_config import MARKET_DATA_METADATA, START_DATE, END_DATE
from etl_config import MARKET_DATA_METADATA
import db_market_data

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

CLIENT = MongoClient(MONGO_CONNECTION_STRING)
DATABASE = CLIENT["coinfolio_prod"]

START_DATE = datetime.date.today() - datetime.timedelta(days=10)
END_DATE = datetime.date.today() - datetime.timedelta(days=1)

# --------------------------------------------------------------------
# STORE MARKET DATA METADATA INFO
# --------------------------------------------------------------------
# print("loading market metadata")
# db_market_data.drop_metadata_collection(DATABASE)
# db_market_data.insert_metadata_list(DATABASE, MARKET_DATA_METADATA)

# --------------------------------------------------------------------
# STORE MARKET DATA QUOTES
# --------------------------------------------------------------------
print("updating market data")

db_market_data.drop_all_series_data_for_date_range(
    DATABASE, START_DATE, END_DATE)

db_market_data.load_all_series(
    DATABASE, MARKET_DATA_METADATA, START_DATE, END_DATE)

CLIENT.close()
