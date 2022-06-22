# import coinfolio_quant.datalake.backtest as datalake_backtest
# import datetime
# import functools
# import os
# from pymongo import MongoClient
# from prettyprinter import pprint
# import pandas as pd
# import numpy as np
# from pymongo import MongoClient
# import coinfolio_quant.datalake.backtest as datalake_backtest
import yfinance as yf
import pandas as pd


# ticker = "XAUUSD=X"
ticker = "GC=F"
# start_date = "2000-01-01"
# start_date = "2020-08-31"
# start_date = "2020-07-10"
start_date = "2020-01-01"
df = yf.download(ticker, start=start_date)
print(df)


# first_date =


# idx = pd.period_range(min(df.index), max(df.index))
idx2 = pd.date_range(min(df.index), max(df.index))

df_reindexed = df.reindex(idx2, method="ffill")

print(df_reindexed)

# print(df.index)
# print(idx)
# print(idx2)
