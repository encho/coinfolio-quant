# import datetime
import os
from turtle import back
from pymongo import MongoClient
from prettyprinter import pprint


# from prettyprinter import pprint
# import pandas as pd
# from coinfolio_quant.datalake.backtest import get_performance_metrics
import coinfolio_quant.datalake.backtest as backtest
import coinfolio_quant.quant_utils.performance_metrics as pmetrics


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


# total_returns = backtest.get_performance_metrics(database, "GOLD_CRYPTO_60_40")
# pprint(metrics)


index_series = backtest.get_performance_total_value_series(
    database, "GOLD_CRYPTO_60_40")
print(index_series)
