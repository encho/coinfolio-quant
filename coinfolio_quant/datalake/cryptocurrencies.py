import pandas as pd


def get_overview(database):
    cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
    print(cryptocurrency_quotes_collection)

    result = database.cryptocurrency_quotes.aggregate(
        [
            {
                "$group":
                {
                    "_id": "$ticker",
                    "min_date": {"$min": "$date"},
                    "max_date": {"$max": "$date"},
                }
            }
        ]
    )

    overview_table = [{"ticker": it["_id"], "min_date": it["min_date"],
                       "max_date": it["max_date"]} for it in result]

    return overview_table


def get_cryptocurrency_dataframe(database, ticker):
    cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
    cursor = cryptocurrency_quotes_collection.find(
        {"ticker": ticker}, {"_id": False})
    results_list = list(cursor)
    df = pd.DataFrame(results_list)
    return df


def get_field_series(database, ticker, field="close"):
    cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
    return_values = {"_id": False, "date": 1, "ticker": 1}
    return_values[field] = 1
    cursor = cryptocurrency_quotes_collection.find(
        {"ticker": ticker}, return_values)

    results_list = list(cursor)

    index = map(lambda it: it["date"], results_list)
    values = map(lambda it: it[field], results_list)

    series = pd.Series(values, index=index)

    return series


def get_field_dataframe(database, tickers, field="close"):
    series_list = [get_field_series(
        database, ticker, field) for ticker in tickers]
    series_dict = dict(zip(tickers, series_list))
    df = pd.DataFrame(series_dict)
    return df


# def get_close_prices(database, tickers):
#     cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
#     cursor = cryptocurrency_quotes_collection.aggregate(
#         [{
#             "$group": {
#                 "_id": "$date"
#             }
#         }]
#         )

#     return list(cursor)


# def get_field_dataframe(database, tickers, field="close"):
#     cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
#     aaa = {"_id": False, "date": 1, "ticker": 1}
#     aaa[field] = 1
#     cursor = cryptocurrency_quotes_collection.find(
#         {"ticker": {"$in": tickers}}, aaa)

#     results_list = list(cursor)
#     # edited_list = map(lambda it: {"date": it.date, })

    # return results_list
