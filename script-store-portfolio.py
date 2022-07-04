# import pandas as pd
# import requests
# import time
# import urllib.parse
# from typing import Optional, Dict, Any, List
# from requests import Request, Session, Response, get
# import hmac
import datetime
from pymongo import MongoClient
import os
from prettyprinter import pprint
from math import floor
from coinfolio_quant.portfolio.rebalancing import create_target_positions, get_total_positions_value, create_liquidations, create_rebalancing_buys
from coinfolio_quant.exchanges.ftx.ftx import FtxClient


target_weights = [{"ticker": "BTC", "weight": 0.5},
                  {"ticker": "ETH", "weight": 0.5}]


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]
FTX_API_KEY = os.environ["FTX_API_KEY"]
FTX_API_SECRET = os.environ["FTX_API_SECRET"]


def make_portfolio_snapshot_item_for_database(api_key, positions):

    portfolio_usd_value = 0
    for position in positions:
        position["usd_value"] = position["usdValue"]
        del position["usdValue"]
        portfolio_usd_value = portfolio_usd_value + position["usd_value"]

    portfolio_item = {
        "api_key": api_key,
        "timestamp": datetime.datetime.now(),
        "usd_value": portfolio_usd_value,
        "positions": positions,
    }
    return portfolio_item


# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]
portfolio_snapshots_collection = database["portfolio_snapshots"]

ftx_client = FtxClient(api_key=FTX_API_KEY, api_secret=FTX_API_SECRET)

positions = ftx_client.get_positions()


pprint(positions)


def persist_portfolio_snapshot(database, ftx_client):
    portfolio_snapshots_collection = database["portfolio_snapshots"]
    api_key = ftx_client._api_key
    positions = ftx_client.get_positions()
    portfolio_snapshot_item = make_portfolio_snapshot_item_for_database(
        api_key, positions)
    portfolio_snapshots_collection.insert_one(portfolio_snapshot_item)


def get_portfolio_snapshots(database, api_key):
    portfolio_snapshots_collection = database["portfolio_snapshots"]
    query_object = {"api_key": api_key}
    result = portfolio_snapshots_collection.find(query_object, {"_id": False})
    return list(result)


# persist_portfolio_snapshot(database, ftx_client)
get_portfolio_snapshots(database, FTX_API_KEY)
