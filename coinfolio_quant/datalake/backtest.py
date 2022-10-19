from prettyprinter import pprint
import pandas as pd
from pymongo import DESCENDING
# import datetime
from ..quant_utils import performance_metrics as pmetrics
from ..quant_utils import date_utils
from .strategies import get_overview


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


# def get_strategy_backtests_series__weights(database, strategy_ticker, start_date=None, end_date=None):
#     query_object = {"strategy_ticker": strategy_ticker}

#     if start_date or end_date:
#         date_query = {}
#         if start_date:
#             date_query["$gte"] = start_date
#         if end_date:
#             date_query["$lte"] = end_date

#         query_object["date"] = date_query

#     result = database.strategies_backtests.find(
#         query_object, {"_id": False, "date": 1, "positions": 1})
#     return list(result)


def get_strategy_backtests_series__all__total_value(database):
    STRATEGIES_OVERVIEW = get_overview(database)
    all_total_value_series = []
    for strategy in STRATEGIES_OVERVIEW:
        total_value_series = get_strategy_backtests_series__total_value(
            database, strategy["ticker"])
        all_total_value_series.append(total_value_series)

    zipped_series = zip(*all_total_value_series)

    result_series = []

    for zipped_series_items in list(zipped_series):
        result_series_item = {"date": zipped_series_items[0]["date"]}
        for (strategy_spec, series_item) in zip(STRATEGIES_OVERVIEW, zipped_series_items):
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

    benchmark_total_values_series = get_performance_total_value_series(
        database, "BITCOIN_ONLY")

    first_timestamp_index = total_values_series.index[0]
    last_timestamp_index = total_values_series.index[-1]

    truncated_benchmark_total_values_series = benchmark_total_values_series.loc[
        first_timestamp_index:last_timestamp_index]

    performance_metrics = pmetrics.series_performance_metrics(
        total_values_series)

    benchmark_performance_metrics = pmetrics.series_performance_metrics(
        truncated_benchmark_total_values_series)

    return {
        "ticker": strategy_ticker,
        "start_date": total_values_series.index[0].to_pydatetime(),
        "end_date": total_values_series.index[-1].to_pydatetime(),
        "performance_metrics": performance_metrics,
        "benchmark_performance_metrics": benchmark_performance_metrics
    }


def get_total_returns_table(database, strategy_ticker):
    total_values_series = get_performance_total_value_series(
        database, strategy_ticker)

    benchmark_total_values_series = get_performance_total_value_series(
        database, "BITCOIN_ONLY")

    first_timestamp_index = total_values_series.index[0]
    last_timestamp_index = total_values_series.index[-1]

    # QTD data
    start_date_QTD_datetime = date_utils.get_first_day_of_the_quarter(
        last_timestamp_index.to_pydatetime())
    start_date_QTD_timestamp = pd.Timestamp(start_date_QTD_datetime)

    cumulative_return_QTD = pmetrics.total_return(
        total_values_series.loc[start_date_QTD_timestamp:])

    benchmark_cumulative_return_QTD = pmetrics.total_return(
        benchmark_total_values_series.loc[start_date_QTD_timestamp:])

    # YTD data
    start_date_YTD_datetime = date_utils.get_first_day_of_the_year(
        last_timestamp_index.to_pydatetime())
    start_date_YTD_timestamp = pd.Timestamp(start_date_YTD_datetime)

    cumulative_return_YTD = pmetrics.total_return(
        total_values_series.loc[start_date_YTD_timestamp:])

    benchmark_cumulative_return_YTD = pmetrics.total_return(
        benchmark_total_values_series.loc[start_date_YTD_timestamp:])

    years_back_to_try = [1, 3, 5, 10]
    annualized_returns_list = []
    for year_back in years_back_to_try:
        year_back_timestamp = pd.Timestamp(date_utils.get_years_back_datetime(
            last_timestamp_index.to_pydatetime(), year_back))
        if first_timestamp_index < year_back_timestamp:
            annualized_returns_list.append({
                "label": f'{year_back}Y',
                "start_date": year_back_timestamp,
                "end_date": last_timestamp_index,
                "percentage_return": pmetrics.annualized_return(
                    total_values_series.loc[year_back_timestamp:], ann_factor=365),
                "benchmark_percentage_return": pmetrics.annualized_return(
                    benchmark_total_values_series.loc[year_back_timestamp:], ann_factor=365),
            })

    # always add since inception
    annualized_returns_list.append({
        "label": "INCEPTION",
        "start_date": first_timestamp_index,
        "end_date": last_timestamp_index,
        "percentage_return": pmetrics.annualized_return(
            total_values_series, ann_factor=365),
        "benchmark_percentage_return": pmetrics.annualized_return(
            benchmark_total_values_series.loc[first_timestamp_index:last_timestamp_index], ann_factor=365),
    })

    return {
        "cumulative_returns": [
            {
                "label": "QTD",
                "start_date": start_date_QTD_timestamp,
                "end_date": last_timestamp_index,
                "percentage_return": cumulative_return_QTD,
                "benchmark_percentage_return": benchmark_cumulative_return_QTD
            },
            {
                "label": "YTD",
                "start_date": start_date_YTD_timestamp,
                "end_date": last_timestamp_index,
                "percentage_return": cumulative_return_YTD,
                "benchmark_percentage_return": benchmark_cumulative_return_YTD
            },
        ],
        "annualized_returns": annualized_returns_list
    }
