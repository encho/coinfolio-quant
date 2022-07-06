import datetime
from operator import index
from pymongo import ASCENDING
import pandas as pd


def make_portfolio_snapshot_item_for_database(client_id, positions):
    portfolio_usd_value = 0
    for position in positions:
        position["usd_value"] = position["usdValue"]
        del position["usdValue"]
        portfolio_usd_value = portfolio_usd_value + position["usd_value"]

    portfolio_item = {
        "client_id": client_id,
        "timestamp": datetime.datetime.now(),
        "usd_value": portfolio_usd_value,
        "positions": positions,
    }
    return portfolio_item


def persist_portfolio_snapshot(database, ftx_client, client_id):
    portfolio_snapshots_collection = database["portfolio_snapshots"]
    api_key = ftx_client._api_key
    positions = ftx_client.get_positions()
    portfolio_snapshot_item = make_portfolio_snapshot_item_for_database(
        client_id, positions)
    result = portfolio_snapshots_collection.insert_one(
        portfolio_snapshot_item)
    return {"_id": result.inserted_id}


def get_portfolio_snapshots(database, client_id):
    portfolio_snapshots_collection = database["portfolio_snapshots"]
    query_object = {"client_id": client_id}
    result = portfolio_snapshots_collection.find(query_object, {"_id": False})
    return list(result)


# TODO test and into library
def resample_irregular_timeseries(irregular_pandas_series, freq="1D", index_key="index", value_key="value"):
    resampled_pandas_series = irregular_pandas_series.resample(
        freq).last().ffill()
    return resampled_pandas_series

# TODO test and into library


def resample_irregular_timeseries_list(data_list, freq="1D", index_key="index", value_key="value"):
    if len(data_list) == 0:
        return []
    index = map(lambda it: it[index_key], data_list)
    values = map(lambda it: it[value_key], data_list)
    irregular_timeseries = pd.Series(values, index=index)
    resampled_timeseries = resample_irregular_timeseries(
        irregular_timeseries, freq=freq, index_key=index_key, value_key=value_key)

    resampled_timeseries_list = [{"index": index, "value": value}
                                 for (index, value) in resampled_timeseries.iteritems()]

    return resampled_timeseries_list


def get_portfolio_value_series(database, client_id):
    portfolio_snapshots_collection = database["portfolio_snapshots"]
    query_object = {"client_id": client_id}
    result = portfolio_snapshots_collection.find(
        query_object, {"_id": False, "usd_value": 1, "timestamp": 1}).sort("timestamp", ASCENDING)
    series_list = list(result)
    index_value_list = list(
        map(lambda it: {"index": it["timestamp"], "value": it["usd_value"]}, series_list))

    resampled_series_list = resample_irregular_timeseries_list(
        index_value_list)

    return resampled_series_list
