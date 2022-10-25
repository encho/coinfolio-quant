import datetime
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
import os
import coinfolio_quant.datalake.analytics_tools as analytics_tools
import coinfolio_quant.quant_utils.date_utils as date_utils

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


def analytics_correlation_tool_endpoint(first_asset, second_asset, date_shift_enum):

    def timeseries_df_to_json(df):
        df["date"] = df.index
        return df.to_json(orient="records")

    today = datetime.datetime(2022, 9, 16)
    start_date = date_utils.get_shifted_date(today, date_shift_enum)

    data = analytics_tools.get_correlation_visualizer_data(
        database, first_asset, second_asset, start_date=start_date, end_date=today)

    result = {
        "first_asset": first_asset,
        "second_asset": second_asset,
        "correlation": data["correlation"],
        "series": timeseries_df_to_json(data["series_df"])
        # "series": data["series_df"]
    }

    return result


result = analytics_correlation_tool_endpoint("BTC", "XAU", "3M")

print(result)
