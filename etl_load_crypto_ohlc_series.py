import yfinance as yf
import pandas as pd
import progressbar
import datetime

# TODO get from one location (deduplicate code)


def parse_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%d")


def run(ohlc_quotes_collection, cryptocurrency, start_date_string, end_date_string):

    start_date = parse_date(start_date_string)
    # trick the yahoo api which would start one day before the passed date
    start_date = start_date + datetime.timedelta(days=1)

    end_date = parse_date(end_date_string)
    # trick the yahoo api which will exclude the end date
    end_date = end_date + datetime.timedelta(days=1)

    ticker = cryptocurrency["ticker"]
    yahoo_ticker = cryptocurrency["yahoo_ticker"]

    print("starting to load: " + cryptocurrency["ticker"])

    # download series data
    df = yf.download(yahoo_ticker, start=start_date, end=end_date)

    # reindex, s.t. we have 7 days a week data
    idx = pd.date_range(min(df.index), max(df.index))
    df = df.reindex(idx, method="ffill")

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
        ohlc_quotes_collection.insert_one(record)

        current_row = current_row + 1
        bar.update(current_row)

    bar.finish()
