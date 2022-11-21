from binance.spot import Spot

# import time
# import urllib.parse
# from typing import Optional, Dict, Any, List
# from requests import Request, Session, Response, get
# import hmac
# from prettyprinter import pprint
# from ...quant_utils import asset_allocation_utils

# from coinfolio_quant.portfolio.rebalancing import create_target_positions, get_total_positions_value, create_liquidations, create_rebalancing_buys


# a mapping which defines which assets on FTX should be taken as a proxy instrument
# for any given key (e.g. "XAU" in our system would be implemented with "PAXG" on FTX exchange)
FTX_ASSET_PROXIES = {"XAU": "PAXG"}


def get_positions(api_key, api_secret, account_name):
    client = Spot(key=api_key, secret=api_secret)

    info = client.account()
    balances = info["balances"]
    parsed_balances = map(lambda balance: {"asset": balance["asset"], "free": float(
        balance["free"]), "locked": float(balance["locked"])}, balances)
    positive_balances = list(filter(
        lambda balance: balance["free"] > 0 or balance["locked"] > 0, parsed_balances))

    assets = list(map(lambda b: b["asset"], positive_balances))

    account_coin = "USDT"

    symbols_for_pricing = [asset + account_coin for asset in assets]
    symbol_prices = client.ticker_price(symbols=symbols_for_pricing)
    parsed_symbol_prices = list(
        map(lambda it: {"symbol": it["symbol"], "price": float(it["price"])}, symbol_prices))

    positions = [
        {"symbol": price["symbol"],
            "asset": balance["asset"],
            "value": (balance["free"] + balance["locked"]) * price["price"],
            "price": float(price["price"])
         } for (balance, price) in zip(positive_balances, parsed_symbol_prices)]

    positions = [
        {
            "ticker": balance["asset"],
            "quantity": (balance["free"] + balance["locked"]),
            # QUICK-FIX better name xxxValue: [20.44, "USDT"]
            "usdValue": (balance["free"] + balance["locked"]) * price["price"],
            "price": float(price["price"])
        } for (balance, price) in zip(positive_balances, parsed_symbol_prices)]

    total_value = 0
    for position in positions:
        total_value += position["usdValue"]

    for position in positions:
        position["weight"] = position["usdValue"] / total_value

    return positions


# def rebalance_portfolio(api_key, api_secret, account_name, target_weights):
#     c = FtxClient(api_key=api_key, api_secret=api_secret,
#                   account_name=account_name)
#     return c.trigger_rebalance(target_weights)


# def get_orders(api_key, api_secret, account_name):
#     c = FtxClient(api_key=api_key, api_secret=api_secret,
#                   account_name=account_name)
#     return c.get_orders()


# def get_orders_history(api_key, api_secret, account_name):
#     c = FtxClient(api_key=api_key, api_secret=api_secret,
#                   account_name=account_name)
#     return c.get_orders_history()


# def get_account(api_key, api_secret, account_name):
#     c = FtxClient(api_key=api_key, api_secret=api_secret,
#                   account_name=account_name)
#     return c.get_account()
