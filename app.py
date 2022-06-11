import os
import json
from pymongo import MongoClient
from flask import Flask
from flask_cors import CORS
from cryptocmd import CmcScraper
import datetime


import coinfolio_quant.datalake.cryptocurrencies as cryptocurrenciesDB
import coinfolio_quant.datalake.strategies as strategiesDB

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]

app = Flask(__name__)

CORS(app)


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


@app.route('/')
def home():
    return "Coinfolio Quant API"


@app.route('/strategies')
def get_strategies():
    strategies_overview = strategiesDB.get_overview(database)
    return json.dumps(strategies_overview, default=default)


@app.route('/strategies/<ticker>')
def get_strategy(ticker):
    strategy_info = strategiesDB.get_strategy_info(database, ticker)
    return json.dumps(strategy_info, default=default)


@app.route('/strategies/series/weights/<ticker>')
def get_strategy_weights_series(ticker):
    strategy_weights_series = strategiesDB.get_strategy_weights_series(
        database, ticker)
    return json.dumps(strategy_weights_series, default=default)


@app.route('/cryptocurrencies')
def cryptocurrencies():
    cryptocurrencies_overview = cryptocurrenciesDB.get_overview(database)
    return json.dumps(cryptocurrencies_overview, default=default)


@app.route('/cryptocurrencies/<ticker>')
def cryptocurrency_series(ticker):
    cryptocurrency_df = cryptocurrenciesDB.get_cryptocurrency_dataframe(
        database, ticker=ticker)

    result = cryptocurrency_df.to_json(orient="table")

    return result


# TODO deprecate, bzw. integrate market cap into etl eventually...
@app.route('/market_capitalization')
def crypto_series():

    scraper = CmcScraper("BTC", "01-01-2022", "03-06-2022")
    df = scraper.get_dataframe()

    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close",
                            "Date": "date", "Volume": "volume", "Market Cap": "capitalization"})

    result = df.to_json(orient="table")

    return result


if __name__ == '__main__':
    app.run()
