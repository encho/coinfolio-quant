import os
import json
from pymongo import MongoClient
from flask import Flask, request
from flask_cors import CORS
from cryptocmd import CmcScraper
import datetime


import coinfolio_quant.datalake.cryptocurrencies as cryptocurrenciesDB
import coinfolio_quant.datalake.strategies as strategiesDB
import coinfolio_quant.datalake.backtest as backtestsDB
import coinfolio_quant.datalake.client_portfolios as clientPortfoliosDB
import coinfolio_quant.exchanges.ftx.ftx as ftxWrapper


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


@app.route('/strategies/series/backtests/<ticker>')
def get_strategy_backtests_series(ticker):
    strategy_backtests_series = backtestsDB.get_strategy_backtests_series(
        database, ticker)
    return json.dumps(strategy_backtests_series, default=default)


@app.route('/strategies/series/backtests/total_value/<ticker>')
def get_strategy_backtests_series__total_value(ticker):
    strategy_backtests_series = backtestsDB.get_strategy_backtests_series__total_value(
        database, ticker)
    return json.dumps(strategy_backtests_series, default=default)


@app.route('/strategies/weights/<ticker>')
def get_strategy_latest_weights(ticker):
    strategy_latest_weights = backtestsDB.get_strategy_latest_weights(
        database, ticker)
    return json.dumps(strategy_latest_weights, default=default)


@app.route('/strategies/performance_metrics/<ticker>')
def get_strategy_performance_metrics(ticker):
    current_strategy_performance_metrics = backtestsDB.get_performance_metrics(
        database, ticker)

    return json.dumps(current_strategy_performance_metrics, default=default)


@app.route('/strategies/total_returns_table/<ticker>')
def get_strategy_total_returns_table(ticker):
    total_returns_table = backtestsDB.get_total_returns_table(
        database, ticker)

    return json.dumps(total_returns_table, default=default)


@app.route('/strategies/series/backtests/total_value')
def get_strategy_backtests_series__all__total_value():
    strategy_backtests_series_dataframe = backtestsDB.get_strategy_backtests_series__all__total_value(
        database)

    result = strategy_backtests_series_dataframe.to_json(orient="split")
    return result


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


@app.route("/ftx/positions")
def ftx_get_positions():

    args = request.args

    # TODO we should return error if these query params are not available!
    api_key = args.get("api_key")
    api_secret = args.get("api_secret")

    result = ftxWrapper.get_positions(api_key=api_key, api_secret=api_secret)

    return json.dumps(result)


@app.route("/ftx/rebalance")
def ftx_rebalance():

    args = request.args

    # TODO we should return error if these query params are not available!
    api_key = args.get("api_key")
    api_secret = args.get("api_secret")

    target_weights = [
        {"ticker": "BTC", "weight": 0.20},
        {"ticker": "SOL", "weight": 0.20},
        {"ticker": "ETH", "weight": 0.20},
        {"ticker": "XRP", "weight": 0.20},
        {"ticker": "LTC", "weight": 0.20},
    ]

    result = ftxWrapper.rebalance_portfolio(
        api_key=api_key, api_secret=api_secret, target_weights=target_weights)

    return json.dumps(result)


@app.route("/ftx/persist_portfolio_snapshot")
def ftx_persist_portfolio_snapshot():

    args = request.args

    # TODO we should return error if these query params are not available!
    api_key = args.get("api_key")
    api_secret = args.get("api_secret")
    user_id = args.get("user_id")

    ftx_client = ftxWrapper.FtxClient(api_key=api_key, api_secret=api_secret)

    clientPortfoliosDB.persist_portfolio_snapshot(
        database=database, ftx_client=ftx_client, client_id=user_id)

    return json.dumps({"status": 200})


@app.route("/ftx/series/portfolio_snapshots")
def ftx_get_portfolio_snapshots():

    args = request.args

    # TODO we should return error if these query params are not available!
    user_id = args.get("user_id")

    portfolio_snapshots = clientPortfoliosDB.get_portfolio_snapshots(
        database=database, client_id=user_id)

    return json.dumps(portfolio_snapshots, default=default)


@app.route("/ftx/series/portfolio_value")
def ftx_get_portfolio_value_series():

    args = request.args

    # TODO we should return error if these query params are not available!
    user_id = args.get("user_id")

    portfolio_value_series = clientPortfoliosDB.get_portfolio_value_series(
        database=database, client_id=user_id)

    return json.dumps(portfolio_value_series, default=default)


if __name__ == '__main__':
    app.run()
