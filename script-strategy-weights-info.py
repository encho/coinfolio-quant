import pandas as pd
import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
import os
from prettyprinter import pprint
import numpy as np

import coinfolio_quant.datalake.backtest as backtest
import coinfolio_quant.datalake.cryptocurrencies as cryptocurrencies


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


def get_strategy_weights_info(database, ticker):
    max_date_result = database.strategies_weights.find(
        {"ticker": ticker}).sort("date", DESCENDING).limit(1)
    min_date_result = database.strategies_weights.find(
        {"ticker": ticker}).sort("date", ASCENDING).limit(1)
    max_date = list(max_date_result)[0]["date"]
    min_date = list(min_date_result)[0]["date"]
    return {
        "max_date": max_date,
        "min_date": min_date,
    }


info = get_strategy_weights_info(database, "CFBG1")

print(info)
