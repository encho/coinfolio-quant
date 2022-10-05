# import datetime
import os
from turtle import back
from pymongo import MongoClient
from prettyprinter import pprint
import datetime
import coinfolio_quant.datalake.market_data as marketDataDB
import numpy as np
import pandas as pd

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]


# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


def na_mask(row):
    price_1 = row[first_asset_ticker]
    price_2 = row[second_asset_ticker]
    if np.isnan(price_1) or np.isnan(price_2):
        return np.nan
    return 1.0


def twr(percentage_return):
    if (np.isnan(percentage_return)):
        return 1
    return 1 + percentage_return


def nan_or_1(val):
    if (np.isnan(val)):
        return np.nan
    return 1


def series_correlation(series_1, series_2):
    series_1.name = "prices_1"
    series_2.name = "prices_2"
    df = pd.concat([series_1, series_2], axis=1)

    def na_mask(row):
        price_1 = row["prices_1"]
        price_2 = row["prices_2"]
        if np.isnan(price_1) or np.isnan(price_2):
            return np.nan
        return 1.0

    df["na_mask"] = df.apply(na_mask, axis=1)
    df["prices_1_masked"] = df["na_mask"] * df["prices_1"]
    df["prices_2_masked"] = df["na_mask"] * df["prices_2"]

    df["prices_1_pct_change__AUXILIARY"] = df["prices_1_masked"].pct_change() * \
        df["prices_1"].apply(nan_or_1)
    df["prices_2_pct_change__AUXILIARY"] = df["prices_2_masked"].pct_change() * \
        df["prices_2"].apply(nan_or_1)
    correlation = df["prices_1_pct_change__AUXILIARY"].corr(
        df["prices_2_pct_change__AUXILIARY"])
    return correlation


start_date = datetime.datetime.today() - datetime.timedelta(days=11)
end_date = datetime.datetime.today() - datetime.timedelta(days=1)

first_asset_ticker = "BTC-USD"
second_asset_ticker = "XAU-USD"

first_asset_ticker_masked = "BTC-USD_MASKED"
second_asset_ticker_masked = "XAU-USD_MASKED"

first_asset_index = first_asset_ticker + "_INDEX"
second_asset_index = second_asset_ticker + "_INDEX"

first_asset_change = first_asset_ticker + "_SHIFT"
second_asset_change = second_asset_ticker + "_SHIFT"

df = marketDataDB.get_field_dataframe(
    database,
    [first_asset_ticker, second_asset_ticker],
    start_date=start_date,
    end_date=end_date
)


# df[first_asset_change] = df[first_asset_index].pct_change()
# df[second_asset_change] = df[second_asset_index].pct_change()
# df[first_asset_change] = df[first_asset_ticker].pct_change()
# df[second_asset_change] = df[second_asset_ticker].pct_change()

# all this just for better correlation number
# ---------------------------------------------------------------------
df["na_mask"] = df.apply(na_mask, axis=1)
df[first_asset_ticker_masked] = df["na_mask"] * df[first_asset_ticker]
df[second_asset_ticker_masked] = df["na_mask"] * df[second_asset_ticker]

df[first_asset_change+"__AUXILIARY"] = df[first_asset_ticker_masked].pct_change() * \
    df[first_asset_ticker].apply(nan_or_1)
df[second_asset_change+"__AUXILIARY"] = df[second_asset_ticker_masked].pct_change() * \
    df[second_asset_ticker].apply(nan_or_1)
correlation = df[first_asset_change +
                 "__AUXILIARY"].corr(df[second_asset_change+"__AUXILIARY"])

# ---------------------------------------------------------------------

# for index calculation (for chart):
df[first_asset_change] = df[first_asset_ticker].pct_change()
df[second_asset_change] = df[second_asset_ticker].pct_change()

df["twr_1"] = df[first_asset_change].apply(twr)
df["twr_2"] = df[second_asset_change].apply(twr)

df["index_1"] = 100 * df["twr_1"].cumprod()
df["index_2"] = 100 * df["twr_2"].cumprod()


print(df)
print("****")
print(correlation)

print("****")
corr_2 = series_correlation(df[first_asset_ticker], df[second_asset_ticker])
print(corr_2)
print("****")
# print(corr_2.iloc[:, 0])
# print("****")
# print(corr_2.iloc[:, 1])
# print("****")

# print(corr_2["prices_1"])
# print("9999")
# print(corr_2["prices_2"])
