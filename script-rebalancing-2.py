import os
from prettyprinter import pprint
from pymongo import MongoClient
from coinfolio_quant.exchanges.ftx.ftx import FtxClient
from coinfolio_quant.portfolio.rebalancing import create_target_positions, get_total_positions_value, create_liquidations, create_rebalancing_buys
import coinfolio_quant.datalake.backtest as backtestsDB


target_weights = [
    {"ticker": "BTC", "weight": 0.50},
    {"ticker": "ETH", "weight": 0.50},
    # {"ticker": "SOL", "weight": 0.20},
    # {"ticker": "XRP", "weight": 0.20},
    # {"ticker": "LTC", "weight": 0.20},
]


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]

strategy_ticker = "CFBG1"

strategy_latest_weights = backtestsDB.get_strategy_latest_weights(
    database, strategy_ticker)["weights"]


pprint(strategy_latest_weights)


FTX_API_KEY = os.environ["FTX_API_KEY"]
FTX_API_SECRET = os.environ["FTX_API_SECRET"]

ftx_client = FtxClient(api_key=FTX_API_KEY, api_secret=FTX_API_SECRET)
# ftx_client.trigger_rebalance(target_weights)
