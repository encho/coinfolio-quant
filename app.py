import pandas as pd
from flask import Flask
from flask_cors import CORS
from cryptocmd import CmcScraper
import yfinance as yf
import json

app = Flask(__name__)
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

CORS(app)

cryptocurrencies_db = [
    {"ticker": "BTC-USD", "base": "BTC", "quote": "USD"},
    {"ticker": "ETH-USD", "base": "ETH", "quote": "USD"},
    {"ticker": "XRP-USD", "base": "XRP", "quote": "USD"},
    {"ticker": "EURUSD=X", "base": "EUR", "quote": "USD"}
]


@app.route('/')
def home():
    df = pd.DataFrame(
        [["a", "b"], ["c", "d"]],
        index=["row 1", "row 2"],
        columns=["col 1", "col 2"],
    )

    result = df.to_json(orient="table")
    return result


@app.route('/series')
def some_example_series():
    my_series = pd.Series([22, 35, 58, 89, 100, 50], name="value", index=pd.to_datetime(
        ["2022-01-01", "2022-01-02", "2022-01-03", "2022-01-04", "2022-01-05", "2022-01-06"]))

    result = my_series.to_json(orient="table")
    return result


@app.route('/cryptoseries')
def crypto_series():

    scraper = CmcScraper("BTC", "01-01-2022", "03-06-2022")
    df = scraper.get_dataframe()

    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close",
                            "Date": "date", "Volume": "volume", "Market Cap": "capitalization"})

    result = df.to_json(orient="table")

    return result


@app.route('/cryptocurrencies')
def cryptocurrencies():
    return json.dumps(cryptocurrencies_db)


@app.route('/cryptocurrencies/<ticker>')
def cryptocurrencies_series(ticker):
    df = yf.download(ticker, start='2022-05-01')

    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close",
                            "Volume": "volume", "Adj Close": "adjusted_close"})

    df.index.names = ['date']

    result = df.to_json(orient="table")

    return result


if __name__ == '__main__':
    app.run()
