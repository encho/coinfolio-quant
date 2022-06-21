# import coinfolio_quant.datalake.cryptocurrencies as cryptocurrencies
# import coinfolio_quant.datalake.strategies as strategies

# import datalake.cryptocurrencies as cryptocurrencies
# import datalake.strategies as strategies

from prettyprinter import pprint
import pandas as pd
import numpy as np
from pymongo import DESCENDING


# TODO into backtest utils package, s.t. the functions can be used everywhere (e.g. etl, scripts, etc..)
def prices_to_returns(prices_series):
    return np.log(prices_series/prices_series.shift())


# TODO into backtest utils package, s.t. the functions can be used everywhere (e.g. etl, scripts, etc..)
def sharpe_ratio(prices_series, ann_factor=365):
    returns_series = prices_to_returns(prices_series)
    sr = returns_series.mean() / returns_series.std()
    ann_sr = sr * ann_factor**0.5
    return ann_sr


# TODO into backtest utils package, s.t. the functions can be used everywhere (e.g. etl, scripts, etc..)
def total_return(prices_series):
    last_price = prices_series.iloc[-1]
    first_price = prices_series.iloc[0]
    return (last_price - first_price) / first_price


# TODO into backtest utils package, s.t. the functions can be used everywhere (e.g. etl, scripts, etc..)
def annualized_return(prices_series, ann_factor=365):
    returns_series = prices_to_returns(prices_series)
    mean_return = returns_series.mean()
    ann_mean_return = ann_factor * mean_return
    return ann_mean_return


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


def get_performance_metrics(database, strategy_ticker):
    backtest_total_value_series = get_strategy_backtests_series__total_value(
        database, strategy_ticker)

    series_dates = [item["date"] for item in backtest_total_value_series]
    series_total_values = [item["total_value"]
                           for item in backtest_total_value_series]

    total_values_series = pd.Series(series_total_values, index=series_dates)

    performance_metrics = {
        "sharpe_ratio": sharpe_ratio(total_values_series),
        "total_return": total_return(total_values_series),
        "annualized_return": annualized_return(total_values_series),
    }

    return {
        "ticker": strategy_ticker,
        "start_date": total_values_series.index[0].to_pydatetime(),
        "end_date": total_values_series.index[-1].to_pydatetime(),
        "performance_metrics": performance_metrics,
    }
