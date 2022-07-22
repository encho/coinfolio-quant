import pandas as pd
import datetime
from pymongo import MongoClient
import os
from prettyprinter import pprint
import numpy as np

import coinfolio_quant.datalake.backtest as backtest
import coinfolio_quant.datalake.cryptocurrencies as cryptocurrencies


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]

# index_series = backtest.get_performance_total_value_series(
#     database, "GOLD_CRYPTO_60_40")

# print(index_series)


def inverted_vola_weightings(list_of_volas):
    denominator = 0
    for vola in list_of_volas:
        denominator = denominator + 1/vola

    weights = [(1/vola) / denominator for vola in list_of_volas]

    return weights


def get_inverted_volatility_asset_allocation(date, universe):
    # TODO include in context
    base_currency = "USD"
    # TODO 360
    vola_days_period = 360

    start_date = date - datetime.timedelta(days=vola_days_period-1)

    price_tickers = list(
        map(lambda ticker: f'{ticker}-{base_currency}', universe))

    data = cryptocurrencies.get_field_dataframe(
        database, price_tickers, field="percentage_change", start_date=start_date, end_date=date)

    # QUICK-FIX we remove the weekdays again which were ffilled before in the etl pipeline
    # TODO: store w/o saturdays and sundays, s.t. this fix is not necessary
    data["weekday"] = pd.to_datetime(data.index).weekday
    data["is_weekday"] = data["weekday"] < 5
    data["quick_fix_factor"] = data["is_weekday"].replace(
        True, 1).replace(False, np.nan)
    data["XAU-USD"] = data["quick_fix_factor"] * data["XAU-USD"]

    data_start_date = data.index[0]
    is_data_valid = data_start_date == start_date

    if is_data_valid:
        std_dev = data.std()
        btc_vola = std_dev["BTC-USD"]
        gold_vola = std_dev["XAU-USD"]
        weights = inverted_vola_weightings([btc_vola, gold_vola])
        return [{"ticker": ticker, "weight": weight} for (ticker, weight) in zip(universe, weights)]

    return [{"ticker": ticker, "weight": np.nan} for ticker in universe]


# inputs
# tickers = ["XAU", "BTC"]
# base_currency = "USD"
# NUMBER_DAYS = 20
# NUMBER_DAYS = 360
# NUMBER_DAYS = 50
# END_DATE = datetime.datetime(2020, 1, 10)
# END_DATE = datetime.datetime(2014, 10, 1)

# START_DATE = END_DATE - datetime.timedelta(days=NUMBER_DAYS-1)

# data = cryptocurrencies.get_field_dataframe(
#     database, ["BTC-USD", "XAU-USD"], field="percentage_change", start_date=START_DATE, end_date=END_DATE)

# QUICK-FIX: put back nan's during weekends for gold
# data["weekday"] = pd.to_datetime(data.index).weekday
# data["is_weekday"] = data["weekday"] < 5
# data["quick_fix_factor"] = data["is_weekday"].replace(
#     True, 1).replace(False, np.nan)

# data["XAU-USD"] = data["quick_fix_factor"] * data["XAU-USD"]

# data_start_date = data.index[0]

# std_dev = data.std()

# btc_vola = std_dev["BTC-USD"]
# gold_vola = std_dev["XAU-USD"]

# print(data)
# print(std_dev)
# print(btc_vola)
# print(gold_vola)

# weights = inverted_vola_weightings([btc_vola, gold_vola])

# print(weights)

# sum_weights = 0
# for w in weights:
#     sum_weights += w

# print(sum_weights)

# is_expected_start_date = data_start_date == START_DATE

# print(is_expected_start_date)


print("********")
date = datetime.datetime(2014, 10, 1)
weights = get_inverted_volatility_asset_allocation(date, ["BTC", "XAU"])
print(weights)
print("********")


print("********")
date = datetime.datetime(2018, 10, 1)
weights = get_inverted_volatility_asset_allocation(date, ["BTC", "XAU"])
print(weights)
print("********")

print("********")
date = datetime.datetime(2019, 10, 1)
weights = get_inverted_volatility_asset_allocation(date, ["BTC", "XAU"])
print(weights)
print("********")


print("********")
date = datetime.datetime(2020, 10, 1)
weights = get_inverted_volatility_asset_allocation(date, ["BTC", "XAU"])
print(weights)
print("********")

print("********")
date = datetime.datetime(2022, 7, 1)
weights = get_inverted_volatility_asset_allocation(date, ["BTC", "XAU"])
print(weights)
print("********")
