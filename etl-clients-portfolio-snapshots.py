import os
from pymongo import MongoClient
from coinfolio_quant.exchanges.binance.persist import persist_all_portfolio_snapshots
from coinfolio_quant.coinfolio_api.coinfolio_api import get_users

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]

users = get_users()
persist_all_portfolio_snapshots(database, users)
