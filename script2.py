# import coinfolio_quant.datalake.backtest as datalake_backtest
# import datetime
# import functools
import os
from statistics import mean
from pymongo import MongoClient
from prettyprinter import pprint
import pandas as pd
import numpy as np
from pymongo import MongoClient
import coinfolio_quant.datalake.backtest as datalake_backtest

# **************************************************************
# THE SCRIPT
# **************************************************************


def prices_to_returns(prices_series):
    return np.log(prices_series/prices_series.shift())


def sharpe_ratio(prices_series, ann_factor=365):
    returns_series = prices_to_returns(prices_series)
    sr = returns_series.mean() / returns_series.std()
    ann_sr = sr * ann_factor**0.5
    return ann_sr


def total_return(prices_series):
    last_price = prices_series.iloc[-1]
    first_price = prices_series.iloc[0]
    return (last_price - first_price) / first_price


def annualized_return(prices_series, ann_factor=365):
    returns_series = prices_to_returns(prices_series)
    mean_return = returns_series.mean()
    ann_mean_return = ann_factor * mean_return
    return ann_mean_return


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


backtest_total_value_series = datalake_backtest.get_strategy_backtests_series__total_value(
    database,
    "G4_EQUALLY_WEIGHTED")


series_dates = [item["date"] for item in backtest_total_value_series]
series_total_values = [item["total_value"]
                       for item in backtest_total_value_series]

total_values_series = pd.Series(series_total_values, index=series_dates)


print("******** metrics are *********")
print(total_values_series)
print(sharpe_ratio(total_values_series))
print(total_return(total_values_series))
print(annualized_return(total_values_series))


def get_performance_metrics(database, strategy_ticker):
    backtest_total_value_series = datalake_backtest.get_strategy_backtests_series__total_value(
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
