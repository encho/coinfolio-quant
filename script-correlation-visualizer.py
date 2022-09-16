# import pandas as pd
# import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
import os
# from prettyprinter import pprint
# import numpy as np

# import coinfolio_quant.datalake.backtest as backtest
import coinfolio_quant.datalake.cryptocurrencies as cryptocurrencies


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


def get_correlation_visualizer_data(database, first_asset, second_asset, time_period):
    # max_date_result = database.strategies_weights.find(
    #     {"ticker": ticker}).sort("date", DESCENDING).limit(1)
    # min_date_result = database.strategies_weights.find(
    #     {"ticker": ticker}).sort("date", ASCENDING).limit(1)
    # max_date = list(max_date_result)[0]["date"]
    # min_date = list(min_date_result)[0]["date"]
    # return {
    #     "max_date": max_date,
    #     "min_date": min_date,
    # }

    # TODO the 'numeraire' (here USD), should also come from the GUI
    first_asset_ticker = first_asset + "-USD"
    second_asset_ticker = second_asset + "-USD"

    first_asset_index = first_asset_ticker + "_INDEX"
    second_asset_index = second_asset_ticker + "_INDEX"

    first_asset_change = first_asset_ticker + "_SHIFT"
    second_asset_change = second_asset_ticker + "_SHIFT"

    df = cryptocurrencies.get_field_dataframe(
        database, [first_asset_ticker, second_asset_ticker], field="close")

    df[first_asset_index] = df[first_asset_ticker] / \
        df[first_asset_ticker].iloc[0]

    df[second_asset_index] = df[second_asset_ticker] / \
        df[second_asset_ticker].iloc[0]

    df[first_asset_change] = df[first_asset_index].pct_change()
    df[second_asset_change] = df[second_asset_index].pct_change()

    correlation = df[first_asset_change].corr(df[second_asset_change])

    series_df = df[[first_asset_index, second_asset_index]]

    return {
        "first_asset": first_asset,
        "second_asset": second_asset,
        "time_period": time_period,
        "correlation": correlation,
        # "series": series_df.to_json(orient="records"),
        # "series": series_df.head().to_json(orient="table"),
        "data": series_df,
    }


data = get_correlation_visualizer_data(database, "BTC", "XAU", "1M")

print(data)
