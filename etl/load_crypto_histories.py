import yfinance as yf
from pymongo import MongoClient
import progressbar
import etl


# TODO eventually close connection at end of script
client = MongoClient(etl.MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]
cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
cryptocurrency_quotes_collection.drop()


def load_crypto_ohlc_series(ohlc_quotes_collection, cryptocurrency, start_date):

    ticker = cryptocurrency["ticker"]

    print("starting to load: " + cryptocurrency["ticker"])

    df = yf.download(ticker, start=start_date)
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close",
                            "Volume": "volume", "Adj Close": "adjusted_close"})
    df.index.names = ['date']

    total_rows = len(df)
    current_row = 0

    bar = progressbar.ProgressBar(maxval=total_rows, widgets=[
                                  progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

    bar.start()

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
        }
        ohlc_quotes_collection.insert_one(record)

        current_row = current_row + 1
        bar.update(current_row)

    bar.finish()


for cryptocurrency in etl.CRYPTOCURRENCIES:
    load_crypto_ohlc_series(
        cryptocurrency_quotes_collection, cryptocurrency, etl.START_DATE)

client.close()