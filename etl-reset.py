import os
import datetime
from pymongo import MongoClient
import datetime

from etl_config import MARKET_DATA_METADATA
import etl_db_market_data

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

CLIENT = MongoClient(MONGO_CONNECTION_STRING)
DATABASE = CLIENT["coinfolio_prod"]

START_DATE = datetime.date(2014, 9, 17)
END_DATE = datetime.date.today() - datetime.timedelta(days=1)

# --------------------------------------------------------------------
# STORE MARKET DATA METADATA INFO
# --------------------------------------------------------------------
print("loading market metadata")
etl_db_market_data.drop_metadata_collection(DATABASE)
etl_db_market_data.insert_metadata_list(DATABASE, MARKET_DATA_METADATA)


# --------------------------------------------------------------------
# STORE MARKET DATA QUOTES
# --------------------------------------------------------------------
print("loading market data")
etl_db_market_data.drop_series_collection(DATABASE)
etl_db_market_data.load_all_series(
    DATABASE, MARKET_DATA_METADATA, START_DATE, END_DATE)


CLIENT.close()
