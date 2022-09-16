# import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

from pymongo import MongoClient, ASCENDING, DESCENDING
import os
# from prettyprinter import pprint
# import numpy as np

# import coinfolio_quant.datalake.backtest as backtest
import coinfolio_quant.datalake.cryptocurrencies as cryptocurrencies
import coinfolio_quant.datalake.analytics_tools as analytics_tools
import coinfolio_quant.quant_utils.date_utils as date_utils

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


# this is the api endpoint function....
today = datetime.datetime(2022, 9, 16)
back_3M = date_utils.get_shifted_date(today, "3M")

data = analytics_tools.get_correlation_visualizer_data(
    database, "BTC", "XAU", start_date=back_3M, end_date=today)

# now, transform to json, to return from api...

print(data)
