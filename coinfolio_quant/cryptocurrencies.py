import pandas as pd


def get_overview(database):
    cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
    print(cryptocurrency_quotes_collection)

    tickers = cryptocurrency_quotes_collection.distinct("ticker")

    # return [
    #     {"ticker": "heheheeheh", "min_date": "hello",
    #         "max_date": "heheheeh", "nr_records": 500},
    #     {"ticker": "heheheeheh", "min_date": "hello",
    #         "max_date": "heheheeh", "nr_records": 500},
    # ]

    # return {"tickers": tickers}

    overview_table = list(map(lambda ticker: {"ticker": ticker}, tickers))

    return overview_table


def get_cryptocurrency_dataframe(database, ticker="hello"):
    cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
    cursor = cryptocurrency_quotes_collection.find(
        {"ticker": ticker}, {"_id": False})
    results_list = list(cursor)
    df = pd.DataFrame(results_list)
    return df
