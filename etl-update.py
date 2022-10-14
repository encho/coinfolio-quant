import os
from pymongo import MongoClient

from etl_config_TEST import MARKET_DATA_METADATA, STRATEGIES_SPECS, UPDATE_START_DATE, UPDATE_END_DATE
import etl_db_market_data
import etl_db_strategy_weights

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

CLIENT = MongoClient(MONGO_CONNECTION_STRING)
DATABASE = CLIENT["coinfolio_prod"]

# --------------------------------------------------------------------
# UPDATE MARKET DATA QUOTES
# --------------------------------------------------------------------
print("updating latest market data")
etl_db_market_data.load_all_series(
    DATABASE, MARKET_DATA_METADATA, UPDATE_START_DATE, UPDATE_END_DATE, upsert=True)

# --------------------------------------------------------------------
# UPDATE STRATEGIES WEIGHTS
# --------------------------------------------------------------------
print("updating latest strategies weights")
etl_db_strategy_weights.load_all_weights_series(
    DATABASE, STRATEGIES_SPECS, UPDATE_START_DATE, UPDATE_END_DATE, upsert=True)


CLIENT.close()
