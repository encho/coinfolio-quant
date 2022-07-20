import pandas as pd
import datetime
from pymongo import MongoClient
import os
from prettyprinter import pprint

import coinfolio_quant.datalake.backtest as backtest
import coinfolio_quant.datalake.cryptocurrencies as cryptocurrencies


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


index_series = backtest.get_performance_total_value_series(
    database, "GOLD_CRYPTO_60_40")

print(index_series)


data = cryptocurrencies.get_field_dataframe(database, ["BTC-USD", "XAU-USD"])

print(data)
