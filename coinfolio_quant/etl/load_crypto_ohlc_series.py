import yfinance as yf
import progressbar


def run(ohlc_quotes_collection, cryptocurrency, start_date):

    ticker = cryptocurrency["ticker"]

    print("starting to load: " + cryptocurrency["ticker"])

    df = yf.download(ticker, start=start_date)
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

    print(df.head())

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
