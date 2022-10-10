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


# TODO sort date ascending
def get_field_series(database, ticker, field="close", start_date=None, end_date=None):
    cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
    return_values = {"_id": False, "date": 1, "ticker": 1}
    return_values[field] = 1

    query_object = {"ticker": ticker}

    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query["$gte"] = start_date
        if end_date:
            date_query["$lte"] = end_date

        query_object["date"] = date_query

    cursor = cryptocurrency_quotes_collection.find(query_object, return_values)

    results_list = list(cursor)

    index = map(lambda it: it["date"], results_list)
    values = map(lambda it: it[field], results_list)

    series = pd.Series(values, index=index)

    return series


def get_field_dataframe(database, tickers, start_date=None, end_date=None, field="close"):
    series_list = [get_field_series(
        database=database, ticker=ticker, field=field, start_date=start_date, end_date=end_date) for ticker in tickers]
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
