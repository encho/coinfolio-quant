import os
import datetime
from pymongo import MongoClient
import datetime

# from etl_config import MARKET_DATA_METADATA, STRATEGIES_SPECS
from etl_config_TEST import MARKET_DATA_METADATA, STRATEGIES_SPECS, RESET_START_DATE, RESET_END_DATE
import etl_db_market_data
import etl_db_strategy_weights


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

CLIENT = MongoClient(MONGO_CONNECTION_STRING)
DATABASE = CLIENT["coinfolio_prod"]

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
    DATABASE, MARKET_DATA_METADATA, RESET_START_DATE, RESET_END_DATE)


# --------------------------------------------------------------------
# STRATEGIES
# --------------------------------------------------------------------
print("loading strategies metadata")
etl_db_strategy_weights.drop_metadata_collection(DATABASE)
etl_db_strategy_weights.insert_metadata_list(DATABASE, STRATEGIES_SPECS)


# --------------------------------------------------------------------
# STORE STRATEGIES WEIGHTS
# --------------------------------------------------------------------
print("loading strategy weights data")
etl_db_strategy_weights.drop_weights_series_collection(DATABASE)


# def load_all_weights_series(DB, SPECS, START, END):
#     dates_list_for_period = get_dates_for_period(START, END)
#     for strategy in SPECS:
#         print("creating strategy weights for strategy: " + strategy["ticker"])
#         for date in dates_list_for_period:
#             etl_db_strategy_weights.create_strategy_weights(DB,
#                                                             strategy["ticker"], date)


# TODO implement
# etl_db_strategy_weights.load_all_weights_series(
#     DATABASE, STRATEGIES_SPECS, RESET_START_DATE, RESET_END_DATE)
etl_db_strategy_weights.load_all_weights_series(
    DATABASE, STRATEGIES_SPECS, RESET_START_DATE, RESET_END_DATE)


CLIENT.close()
