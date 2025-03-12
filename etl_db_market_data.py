import datetime
import yfinance as yf
import progressbar
import datetime


def series_collection(database):
    return database["market_data_series"]


def metadata_collection(database):
    return database["market_data_metadata"]


def drop_metadata_collection(database):
    metadata_collection(database).drop()


def drop_series_collection(database):
    series_collection(database).drop()


def insert_metadata_list(database, metadata_list):
    for metadata_record in metadata_list:
        metadata_collection(database).insert_one(metadata_record)


# TODO actually metadata should be taken from database
def load_all_series(database, metadata_list, start_date, end_date, upsert=False):
    for metadata_record in metadata_list:
        fetch_and_store_series(database, metadata_record,
                               start_date, end_date, upsert=upsert)


def drop_all_series_data_for_date_range(database, start_date, end_date):
    start_datetime = datetime.datetime.combine(
        start_date, datetime.datetime.min.time())
    end_datetime = datetime.datetime.combine(
        end_date, datetime.datetime.min.time())

    result = series_collection(database).delete_many({
        "date": {
            "$lte": end_datetime,
            "$gte": start_datetime,
        }
    })

    print(f'{result.deleted_count} series items deleted')


def fetch_and_store_series(database, market_data_spec, start_date, end_date, upsert=False):

    market_data_series_collection = series_collection(database)

    # trick the yahoo api which would start one day before the passed date
    start_date = start_date + datetime.timedelta(days=1)

    # trick the yahoo api which will exclude the end date
    end_date = end_date + datetime.timedelta(days=1)

    ticker = market_data_spec["ticker"]
    yahoo_ticker = market_data_spec["yahoo_ticker"]

    print("starting to load: " + market_data_spec["ticker"])

    # download series data
    df = yf.download(yahoo_ticker, start=start_date, end=end_date, auto_adjust=False)

    df.columns = df.columns.droplevel(1)


    # rename columns
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close",
                            "Volume": "volume", "Adj Close": "adjusted_close"})
    df.index.names = ['date']

    df["percentage_change"] = (df['close'] /
                               df['close'].shift(1) - 1).fillna(0)

    df["adjusted_percentage_change"] = (df["adjusted_close"] /
                                        df["adjusted_close"].shift(1) - 1).fillna(0)

    total_rows = len(df)
    current_row = 0

    bar = progressbar.ProgressBar(maxval=total_rows, widgets=[
        progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

    bar.start()

    print(df)

    for index, row in df.iterrows():

        record = {
            "ticker": ticker,
            "date": index,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
            "adjusted_close": row.adjusted_close,
            "percentage_change": row.percentage_change,
            "adjusted_percentage_change": row.adjusted_percentage_change,
        }

        if upsert == False:
            market_data_series_collection.insert_one(record)
        else:
            market_data_series_collection.update_one({"ticker": ticker, "date": index},
                                                     {"$set": record}, upsert=True
                                                     )

        current_row = current_row + 1
        bar.update(current_row)

    bar.finish()
