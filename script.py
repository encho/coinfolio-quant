# import os
# from pymongo import MongoClient
# import pandas as pd
# import coinfolio_quant.datalake.cryptocurrencies as crypto
import datetime

# MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# client = MongoClient(MONGO_CONNECTION_STRING)
# database = client["coinfolio_prod"]

START_DATE = "2022-06-01"

date = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")

print(START_DATE)
print(date)

date_2 = date + datetime.timedelta(days=1)
date_3 = date + datetime.timedelta(days=2)
print(date_2)
print(date_3)


def get_dates_until_today(date_string):
    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    dates = [date]
    current_date = date

    today_at_midnight = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)

    while current_date < today_at_midnight:
        next_day = current_date + datetime.timedelta(days=1)
        dates.append(next_day)
        current_date = next_day
    return dates


dates = get_dates_until_today(START_DATE)

print(dates)
