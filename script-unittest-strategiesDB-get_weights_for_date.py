import os
import datetime
from prettyprinter import pprint
from pymongo import MongoClient

import coinfolio_quant.datalake.strategies as strategiesDB

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]

date = datetime.datetime(2022, 10, 10)
strategy_ticker = "CFBG1"

weights = strategiesDB.get_strategy_weights_for_date(database, "CFBG1", date)

assert(type(weights["weights"]) == list)

client.close()
