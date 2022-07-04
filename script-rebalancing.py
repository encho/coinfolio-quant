import os
from prettyprinter import pprint
from math import floor
from coinfolio_quant.portfolio.rebalancing import create_target_positions, get_total_positions_value, create_liquidations, create_rebalancing_buys
from coinfolio_quant.exchanges.ftx.ftx import FtxClient


target_weights = [{"ticker": "BTC", "weight": 0.5},
                  {"ticker": "ETH", "weight": 0.5}]


FTX_API_KEY = os.environ["FTX_API_KEY"]
FTX_API_SECRET = os.environ["FTX_API_SECRET"]

ftx_client = FtxClient(api_key=FTX_API_KEY, api_secret=FTX_API_SECRET)
ftx_client.trigger_rebalance(target_weights)
