import os
from pymongo import MongoClient
import pandas as pd
import coinfolio_quant.datalake.cryptocurrencies as crypto

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]

print("===== the script =====")

ohlc_df = crypto.get_cryptocurrency_dataframe(
    database, ticker="BTC-USD")

print(ohlc_df.head())
