from cmath import nan
from prettyprinter import pprint
import pandas as pd
import numpy as np
from pymongo import DESCENDING
from ..quant_utils import performance_metrics as pmetrics


# TODO sort date ascending
def get_strategy_backtests_series(database, strategy_ticker, start_date=None, end_date=None):
    query_object = {"strategy_ticker": strategy_ticker}

    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query["$gte"] = start_date
        if end_date:
            date_query["$lte"] = end_date

        query_object["date"] = date_query

    result = database.strategies_backtests.find(query_object, {"_id": False})
    return list(result)


def get_strategy_backtests_series__total_value(database, strategy_ticker, start_date=None, end_date=None):
    query_object = {"strategy_ticker": strategy_ticker}

    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query["$gte"] = start_date
        if end_date:
            date_query["$lte"] = end_date

        query_object["date"] = date_query

    result = database.strategies_backtests.find(
        query_object, {"_id": False, "date": 1, "total_value": 1})
    return list(result)


# TODO: import strategies db module, s.t. etl also still works (and scripts!!!!)
STRATEGIES = [
    {
        "ticker": "G4_EQUALLY_WEIGHTED",
        "name": "Equally Weighted G4 Basket",
        "description": "Equally weighted portfolio of 4 main cryptocurrencies.",
    },
    {
        "ticker": "G2_EQUALLY_WEIGHTED",
        "name": "Equally Weighted G2 Basket",
        "description": "Equally weighted portfolio of 2 main cryptocurrencies.",
    },
    {
        "ticker": "GOLD_CRYPTO_50_50",
        "name": "Gold & Bitcoin 50-50 Basket",
        "description": "Gold & Bitcoin Portfolio 50%-50%",
    },
    {
        "ticker": "GOLD_CRYPTO_60_40",
        "name": "Gold & Bitcoin 60-40 Basket",
        "description": "Gold & Bitcoin Portfolio 60%-40%",
    },
    {
        "ticker": "GOLD_CRYPTO_70_30",
        "name": "Gold & Bitcoin 70-30 Basket",
        "description": "Gold & Bitcoin Portfolio 70%-30%",
    },
    {
        "ticker": "COINFOLIO_GOLD_CRYPTO",
        "name": "Gold Crypto",
        "description": "Gold & Crypto Portfolio",
    }
]


def get_strategy_backtests_series__all__total_value(database):
    all_total_value_series = []
    for strategy in STRATEGIES:
        total_value_series = get_strategy_backtests_series__total_value(
            database, strategy["ticker"])
        all_total_value_series.append(total_value_series)

    zipped_series = zip(*all_total_value_series)

    result_series = []

    for zipped_series_items in list(zipped_series):
        result_series_item = {"date": zipped_series_items[0]["date"]}
        for (strategy_spec, series_item) in zip(STRATEGIES, zipped_series_items):
            result_series_item[strategy_spec["ticker"]
                               ] = series_item["total_value"]
            result_series.append(result_series_item)

    return pd.DataFrame(result_series)


# TODO into strategies file
def get_strategy_latest_weights(database, strategy_ticker):
    result = database.strategies_weights.find(
        {"ticker": strategy_ticker}, {"_id": False}).sort("date", DESCENDING).limit(1)

    result_list = list(result)
    return result_list[0]


def get_performance_total_value_series(database, strategy_ticker):
    backtest_total_value_series = get_strategy_backtests_series__total_value(
        database, strategy_ticker)

    series_dates = [item["date"] for item in backtest_total_value_series]
    series_total_values = [item["total_value"]
                           for item in backtest_total_value_series]

    total_values_series = pd.Series(series_total_values, index=series_dates)

    return total_values_series


def get_performance_metrics(database, strategy_ticker):
    total_values_series = get_performance_total_value_series(
        database, strategy_ticker)

    performance_metrics = pmetrics.series_performance_metrics(
        total_values_series)

    return {
        "ticker": strategy_ticker,
        "start_date": total_values_series.index[0].to_pydatetime(),
        "end_date": total_values_series.index[-1].to_pydatetime(),
        "performance_metrics": performance_metrics,
    }
