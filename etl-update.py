import os
import datetime
from pymongo import MongoClient
import datetime

# from etl_config import MARKET_DATA_METADATA, START_DATE, END_DATE
from etl_config import MARKET_DATA_METADATA
import etl_db_market_data

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

CLIENT = MongoClient(MONGO_CONNECTION_STRING)
DATABASE = CLIENT["coinfolio_prod"]

START_DATE = datetime.date.today() - datetime.timedelta(days=10)
END_DATE = datetime.date.today() - datetime.timedelta(days=1)

# --------------------------------------------------------------------
# STORE MARKET DATA QUOTES
# --------------------------------------------------------------------
print("updating latest market data")
etl_db_market_data.load_all_series(
    DATABASE, MARKET_DATA_METADATA, START_DATE, END_DATE, upsert=True)

CLIENT.close()
