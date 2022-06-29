# import pandas as pd
# import requests
# import time
# import urllib.parse
# from typing import Optional, Dict, Any, List
# from requests import Request, Session, Response, get
# import hmac
# import os
from prettyprinter import pprint
# from coinfolio_quant.portfolio.backtest import create_rebalancing_list


strategy_item = {
    "ticker": "G4_EQUALLY_WEIGHTED",
    "date": "2022-06-21T00:00:00",
    "weights": [
        {
            "ticker": "BTC",
            "weight": 0.25
        },
        {
            "ticker": "ETH",
            "weight": 0.25
        },
        {
            "ticker": "XRP",
            "weight": 0.25
        },
        {
            "ticker": "ADA",
            "weight": 0.25
        }
    ]
}

# TODO to be coherent we should have the positins field called "usd_value"
positions = [
    {
        "ticker": "BTC",
        "quantity": 0.00325424,
        "usdValue": 65.29813325109174,
        "weight": 0.6562123263727936
    },
    {
        "ticker": "ETH",
        "quantity": 0.021,
        "usdValue": 23.74449,
        "weight": 0.2386197927208742
    },
    {
        "ticker": "EURT",
        "quantity": 10.00000626,
        "usdValue": 10.46500656139052,
        "weight": 0.10516788090633214
    }
]


# TODO to be coherent we should have the positins field called "usd_value"
def create_target_positions(target_weights, portfolio_value_in_usd, instrument_prices_in_usd):

    target_positions = [{"ticker": it["ticker"],
                         "weight": it["weight"],
                        #  usd value just auxiliary
                         "usdValue": it["weight"] * portfolio_value_in_usd,
                         "quantity": (it["weight"] * portfolio_value_in_usd) / instrument_prices_in_usd[it["ticker"] + "-USD"]
                         } for it in target_weights]

    return target_positions


test_target_weights = [{"ticker": "BTC", "weight": 0.4}, {
    "ticker": "ETH", "weight": 0.6}]
test_portfolio_value_in_usd = 1000
test_instrument_prices_in_usd = {"BTC-USD": 10, "ETH-USD": 1}

test_target_positions = create_target_positions(
    test_target_weights, test_portfolio_value_in_usd, test_instrument_prices_in_usd)

assert(test_target_positions == [
    {
        'ticker': 'BTC',
        'weight': 0.4,
        'usdValue': 400.0,
        'quantity': 40.0
    },
    {
        'ticker': 'ETH',
        'weight': 0.6,
        'usdValue': 600.0,
        'quantity': 600.0
    }
])

pprint(test_target_positions)
