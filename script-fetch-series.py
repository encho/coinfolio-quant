from pymongo import MongoClient
import os
import coinfolio_quant.datalake.market_data as marketDataDB

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]

spx_close = marketDataDB.get_field_series(database, "SPX_INDEX")
btc_usd_close = marketDataDB.get_field_series(database, "BTC-USD")

print(spx_close)
print(btc_usd_close)

client.close()
