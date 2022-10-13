import pandas as pd

# TODO eventually into utils
# TODO more performant, return as soon as first is found


def find_unique(predicate, data):
    filtered_items = list(filter(predicate, data))

    if len(filtered_items) != 1:
        raise Exception(
            "Could not find exaclty one match for the predicate.")

    return filtered_items[0]


def get_overview_list(database):
    market_data_series_collection = database["market_data_series"]

    result = market_data_series_collection.aggregate(
        [
            {
                "$group":
                {
                    "_id": "$ticker",
                    "min_date": {"$min": "$date"},
                    "max_date": {"$max": "$date"},
                    "count": {"$sum": 1}
                }
            }
        ]
    )

    dates_info_list = [{"ticker": it["_id"], "min_date": it["min_date"],
                       "max_date": it["max_date"], "count": it["count"]} for it in result]

    metadata_list = get_metadata_list(database)

    overview_list = []
    for metadata_item in metadata_list:
        dates_info = find_unique(
            lambda it: it["ticker"] == metadata_item["ticker"], dates_info_list)
        merged_item = dict()
        merged_item.update(metadata_item)
        merged_item.update(dates_info)
        overview_list.append(merged_item)

    return overview_list


def get_metadata_list(database):
    market_data_metatdata_collection = database["market_data_metadata"]
    cursor = market_data_metatdata_collection.find({}, {"_id": False})
    results_list = list(cursor)
    return results_list


# TODO remove from cryptocurrencies module
# TODO deprecate
def get_timeseries_metadata_list(database):
    market_data_metatdata_collection = database["market_data_metadata"]
    cursor = market_data_metatdata_collection.find({}, {"_id": False})
    results_list = list(cursor)
    return results_list


# TODO remove from cryptocurrencies module
# TODO rename to get_metadata
def get_timeseries_metadata(database, ticker):
    market_data_metatdata_collection = database["market_data_metadata"]
    cursor = market_data_metatdata_collection.find(
        {"ticker": ticker}, {"_id": False})
    results_list = list(cursor)
    return results_list[0]


def get_dataframe(database, ticker):
    market_data_series_collection = database["market_data_series"]
    cursor = market_data_series_collection.find(
        {"ticker": ticker}, {"_id": False})
    results_list = list(cursor)
    df = pd.DataFrame(results_list)
    return df


# TODO sort date ascending
def get_field_series(database, ticker, field="close", start_date=None, end_date=None):
    market_data_series_collection = database["market_data_series"]
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

    cursor = market_data_series_collection.find(query_object, return_values)

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
