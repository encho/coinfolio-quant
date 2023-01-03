import datetime
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
import os
import time
import coinfolio_quant.datalake.analytics_tools as analytics_tools
import coinfolio_quant.quant_utils.date_utils as date_utils

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]

end_date_iso_string = "2023-01-02T10:58:07.898Z"
time_period_shift = "3M"

end_date = datetime.datetime(
    *time.strptime(end_date_iso_string, "%Y-%m-%dT%H:%M:%S.%f%z")[:6])
start_date = date_utils.get_shifted_date(end_date, time_period_shift)

result = analytics_tools.get_correlation_visualizer_data(
    database, "BTC-USD", "ETH-USD", start_date, end_date)

df = result['series_df']

print(df)
