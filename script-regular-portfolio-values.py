import datetime
from pymongo import MongoClient
import os
from prettyprinter import pprint
import pandas as pd
from coinfolio_quant.datalake.client_portfolios import get_portfolio_value_series


# TODO test and into library
def resample_irregular_timeseries(irregular_pandas_series, freq="1D", index_key="index", value_key="value"):
    resampled_pandas_series = irregular_pandas_series.resample(
        freq).last().ffill()
    return resampled_pandas_series

# TODO test and into library


def resample_irregular_timeseries_list(data_list, freq="1D", index_key="index", value_key="value"):
    index = map(lambda it: it[index_key], data_list)
    values = map(lambda it: it[value_key], data_list)
    irregular_timeseries = pd.Series(values, index=index)
    return resample_irregular_timeseries(irregular_timeseries, freq=freq, index_key=index_key, value_key=value_key)


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]
# portfolio_snapshots_collection = database["portfolio_snapshots"]

# portfolio_value_series = get_portfolio_value_series(
#     database=database, client_id="cl4r3ke0t0012elrcos2suy3h")


# index = map(lambda it: it["timestamp"], portfolio_value_series)
# values = map(lambda it: it["usd_value"], portfolio_value_series)

# series = pd.Series(values, index=index)


# pprint(portfolio_value_series)

# print("************")
# print(series)
# print("~~~~~~~")
# print(resample_irregular_timeseries(series))

# series_2 = series.resample('1D').ffill()
# series_3 = series.resample('1D').bfill()
# series_4 = series.resample('1D').last()

# print(series_2)
# print(series_3)
# print(series_4)


# create an irregularly spaced series with some holes, to inspect resampling efficacy for our case
# index = [
#     datetime.datetime.strptime("01/01/20 01:55:19", "%d/%m/%y %H:%M:%S"),
#     datetime.datetime.strptime("01/01/20 02:00:19", "%d/%m/%y %H:%M:%S"),
#     datetime.datetime.strptime("01/01/20 23:00:00", "%d/%m/%y %H:%M:%S"),
#     datetime.datetime.strptime("02/01/20 23:00:00", "%d/%m/%y %H:%M:%S"),
#     datetime.datetime.strptime("04/01/20 23:00:00", "%d/%m/%y %H:%M:%S"),
#     datetime.datetime.strptime("04/01/20 23:10:00", "%d/%m/%y %H:%M:%S"),
#     datetime.datetime.strptime("04/01/20 23:11:00", "%d/%m/%y %H:%M:%S"),
#     datetime.datetime.strptime("04/01/20 23:11:02", "%d/%m/%y %H:%M:%S"),
#     datetime.datetime.strptime("04/01/20 23:11:03", "%d/%m/%y %H:%M:%S"),
#     datetime.datetime.strptime("04/01/20 23:11:04", "%d/%m/%y %H:%M:%S"),
# ]
# values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# series = pd.Series(values, index=index)

# series_test = series.resample('1D').last().ffill()

# print("*****")
# print(series)
# print("-----")
# print(resample_irregular_timeseries(series))


portfolio_value_series = get_portfolio_value_series(
    database=database, client_id="cl4r3ke0t0012elrcos2suy3h")

print(portfolio_value_series)


portfolio_value_series = get_portfolio_value_series(
    database=database, client_id="cl4r3ke0t0012elrcos2suy3h----------")

print(portfolio_value_series)
