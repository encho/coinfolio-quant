import functools
from pymongo import ASCENDING, DESCENDING


def get_overview(database):
    result = database.strategies.find()
    return list(result)


def get_strategy_info(database, ticker):
    result = database.strategies.find_one({"ticker": ticker})
    return result


def get_strategy_weights_info(database, ticker):
    max_date_result = database.strategies_weights.find(
        {"ticker": ticker}).sort("date", DESCENDING).limit(1)
    min_date_result = database.strategies_weights.find(
        {"ticker": ticker}).sort("date", ASCENDING).limit(1)
    max_date = list(max_date_result)[0]["date"]
    min_date = list(min_date_result)[0]["date"]
    return {
        "max_date": max_date,
        "min_date": min_date,
    }


# TODO sort date ascending
def get_strategy_weights_series(database, ticker, start_date=None, end_date=None):
    query_object = {"ticker": ticker}

    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query["$gte"] = start_date
        if end_date:
            date_query["$lte"] = end_date

        query_object["date"] = date_query

    result = database.strategies_weights.find(query_object)
    return list(result)


def get_strategy_tickers(database, ticker, start_date=None, end_date=None):
    query_object = {"ticker": ticker}

    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query["$gte"] = start_date
        if end_date:
            date_query["$lte"] = end_date

        query_object["date"] = date_query

    tickers = functools.reduce(
        lambda all_keys, rec_keys: all_keys | set(rec_keys),
        map(lambda d: map(
            lambda it: it["ticker"], d["weights"]), database.strategies_weights.find(query_object)),
        set()
    )
    return list(tickers)
