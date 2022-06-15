import functools


def get_overview(database):
    result = database.strategies.find()
    return list(result)


def get_strategy_info(database, ticker):
    result = database.strategies.find_one({"ticker": ticker})
    print(result)
    return result


def get_strategy_weights_series(database, ticker):
    result = database.strategies_weights.find({"ticker": ticker})
    return list(result)


def get_strategy_tickers(database, ticker):
    tickers = functools.reduce(
        lambda all_keys, rec_keys: all_keys | set(rec_keys),
        map(lambda d: map(
            lambda it: it["ticker"], d["weights"]), database.strategies_weights.find({"ticker": ticker})),
        set()
    )
    return list(tickers)
