import os
import datetime
from prettyprinter import pprint
from pymongo import MongoClient

import coinfolio_quant.datalake.strategies as strategiesDB
import coinfolio_quant.datalake.market_data as marketDataDB

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]

date = datetime.datetime(2022, 10, 9)

prices = marketDataDB.get_field_dict_for_date(
    database, ["XAU-USD", "BTC-USD"], date, "close")

assert(type(prices["XAU-USD"]) == float)
assert(type(prices["BTC-USD"]) == float)


client.close()
