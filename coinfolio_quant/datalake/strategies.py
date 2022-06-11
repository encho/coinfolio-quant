
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
