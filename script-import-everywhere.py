# import datetime
import os
from pymongo import MongoClient
from prettyprinter import pprint


# from prettyprinter import pprint
# import pandas as pd
# from coinfolio_quant.datalake.backtest import get_performance_metrics
import coinfolio_quant.datalake.backtest as backtest
import coinfolio_quant.quant_utils.performance_metrics as pmetrics


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


print(database)


metrics = backtest.get_performance_metrics(database, "GOLD_CRYPTO_60_40")
pprint(metrics)

performance_series = backtest.get_performance_total_value_series(
    database, "GOLD_CRYPTO_60_40")


pprint(performance_series)


# g = performance_series.groupby(
#     [performance_series.index.year, performance_series.index.month])
#
# grouped_df = g.agg(["first", "last"])

# pprint(g)
# pprint(grouped_df)
# grouped_df.index.rename(["year", "month"], inplace=True)


# grouped_df["monthly_return"] = (
#     grouped_df["last"] - grouped_df["first"]) / grouped_df["first"]
# pprint(grouped_df)


# grouped_df["monthly_return"].idxmax()
# Out[10]: (2020, 12)

# In [22]: grouped_df.loc[(2022, 6),:]
# Out[22]:
# first             22305.462983
# last              19332.160218
# monthly_return       -0.133299
# Name: (2022, 6), dtype: float64

# In [23]: grouped_df.loc[(2022, 6),"monthly_return"]
# Out[23]: -0.1332993073073529

aa = pmetrics.monthly_returns_multiindex_df(performance_series)

print(aa)

max_index = aa["percentage_change"].idxmax()
min_index = aa["percentage_change"].idxmin()

max_item = aa.loc[max_index, :]

print(max_item)
# print(max_item["year"])
# print(max_item["month"])
# print(max_item["percentage_change"])

# print(aa.loc[min_index, :])
