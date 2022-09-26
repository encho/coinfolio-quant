import os
import json
from pymongo import MongoClient
from flask import Flask, request
from flask_cors import CORS
from cryptocmd import CmcScraper
import datetime
import time
# from prettyprinter import pprint


import coinfolio_quant.datalake.cryptocurrencies as cryptocurrenciesDB
import coinfolio_quant.datalake.strategies as strategiesDB
import coinfolio_quant.datalake.backtest as backtestsDB
import coinfolio_quant.datalake.analytics_tools as analyticsToolsDB
import coinfolio_quant.datalake.client_portfolios as clientPortfoliosDB
import coinfolio_quant.exchanges.ftx.ftx as ftxWrapper
import coinfolio_quant.quant_utils.date_utils as date_utils


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


@app.route('/timeseriesdata')
def cryptocurrencies_list():
    timeseriesdata_list = cryptocurrenciesDB.get_timeseriesdata_list(
        database)
    return json.dumps(timeseriesdata_list, default=default)


# TODO: rename to cryptocurrencies/dates-overview or so
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

    # TODO get user id from secure! JWT token and then use the JWT to retrieve api_key, api_secret and strategy_ticker for user from coinfolio js api!!

    # TODO we should return error if these query params are not available!
    api_key = args.get("api_key")
    api_secret = args.get("api_secret")

    # QUICK-FIX: this fixture will need to change once we have multiple strategies in the retail app
    strategy_ticker = "CFBG1"

    strategy_latest_weights = backtestsDB.get_strategy_latest_weights(
        database, strategy_ticker)

    target_weights = strategy_latest_weights["weights"]

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


@app.route("/analytics-tools/correlation-visualizer")
def analytics_tools_correlation_visualizer():

    args = request.args

    # TODO we should return error if these query params are not available!
    first_asset = args.get("firstAsset")
    second_asset = args.get("secondAsset")
    end_date_iso_string = args.get("endDate")
    time_period_shift = args.get("timePeriod")

    def timeseries_df_to_json(df):
        df["date"] = df.index
        return df.to_json(orient="records")

    end_date = datetime.datetime(
        *time.strptime(end_date_iso_string, "%Y-%m-%dT%H:%M:%S.%f%z")[:6])
    start_date = date_utils.get_shifted_date(end_date, time_period_shift)

    data = analyticsToolsDB.get_correlation_visualizer_data(
        database, first_asset, second_asset, start_date=start_date, end_date=end_date)

    result = {
        "first_asset": first_asset,
        "second_asset": second_asset,
        "start_date": start_date,
        "end_date": end_date,
        "time_period": time_period_shift,
        "correlation": data["correlation"],
        "series": timeseries_df_to_json(data["series_df"])
    }

    print(result)

    return json.dumps(result, default=default)


if __name__ == '__main__':
    app.run()
