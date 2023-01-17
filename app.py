import os
# TODO deprecate json in favor of simplejson (used below)
import json
from pymongo import MongoClient
from flask import Flask, request
from flask_cors import CORS
from cryptocmd import CmcScraper
import datetime
import time
import simplejson
import urllib

import coinfolio_quant.datalake.market_data as marketDataDB
import coinfolio_quant.datalake.strategies as strategiesDB
import coinfolio_quant.datalake.backtest as backtestsDB
import coinfolio_quant.datalake.analytics_tools as analyticsToolsDB
import coinfolio_quant.datalake.client_portfolios as clientPortfoliosDB
import coinfolio_quant.exchanges.binance.binance as Binance
from coinfolio_quant.exchanges.binance.persist import persist_all_portfolio_snapshots as binance_persist_all_portfolio_snapshots
import coinfolio_quant.quant_utils.date_utils as date_utils
import coinfolio_quant.quant_utils.series_warnings as series_warnings
from coinfolio_quant.coinfolio_api.coinfolio_api import get_users as coinfolio_get_users


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

    json_result = simplejson.dumps(strategy_weights_series, ignore_nan=True,
                                   default=datetime.datetime.isoformat)

    return json_result


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
    timeseriesdata_list = marketDataDB.get_metadata_list(
        database)
    return json.dumps(timeseriesdata_list, default=default)


@app.route('/market-data/metadata')
def get_market_data_metadata_list():
    metadata_list = marketDataDB.get_metadata_list(
        database)
    return json.dumps(metadata_list, default=default)

@app.route('/market-data/metadata2')
def get_market_data_metadata_list_2():
    metadata_list = marketDataDB.get_metadata_list_2(
        database)
    return json.dumps(metadata_list, default=default)


@app.route('/market-data/overview')
def get_market_data_overview_list():
    overview_list = marketDataDB.get_overview_list(
        database)
    return json.dumps(overview_list, default=default)

# TODO add date range to query params


@app.route('/market-data/dataframe/<ticker>')
def get_market_data_dataframe(ticker):
    df = marketDataDB.get_dataframe(
        database, ticker=ticker)

    result = df.to_json(orient="table")

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


@app.route("/binance/series/portfolio_value")
def binance_get_portfolio_value_series():

    args = request.args

    # TODO we should return error if these query params are not available!
    user_id = args.get("user_id")

    portfolio_value_series = clientPortfoliosDB.get_portfolio_value_series(
        database=database, client_id=user_id)

    return json.dumps(portfolio_value_series, default=default)


@app.route("/binance/positions")
def binance_get_positions():
    args = request.args

    # TODO we should return error if these query params are not available!
    api_key = args.get("api_key")
    api_secret = args.get("api_secret")
    account_name = urllib.parse.unquote(args.get("account_name"))

    result = Binance.get_positions(
        api_key=api_key, api_secret=api_secret, account_name=account_name)

    return json.dumps(result)


@app.route("/binance/persist_portfolio_snapshot")
def binance_persist_portfolio_snapshot():

    args = request.args

    # TODO we should return error if these query params are not available!
    api_key = args.get("api_key")
    api_secret = args.get("api_secret")
    account_name = urllib.parse.unquote(args.get("account_name"))
    user_id = args.get("user_id")

    positions = Binance.get_positions(
        api_key=api_key, api_secret=api_secret, account_name=account_name)

    clientPortfoliosDB.persist_portfolio_snapshot(
        database=database, positions=positions, client_id=user_id)

    return json.dumps({"status": 200})


@app.route("/binance/orders/history")
def binance_get_orders_history():

    args = request.args

    # TODO we should return error if these query params are not available!
    api_key = args.get("api_key")
    api_secret = args.get("api_secret")
    account_name = urllib.parse.unquote(args.get("account_name"))

    result = Binance.get_orders_history(
        api_key=api_key, api_secret=api_secret, account_name=account_name)

    json_result = json.dumps(result)
    return json_result


@app.route("/binance/rebalance")
def binance_rebalance():

    args = request.args

    # TODO get user id from secure! JWT token and then use the JWT to retrieve api_key, api_secret and strategy_ticker for user from coinfolio js api!!

    # TODO we should return error if these query params are not available!
    api_key = args.get("api_key")
    api_secret = args.get("api_secret")
    account_name = urllib.parse.unquote(args.get("account_name"))

    # QUICK-FIX: this fixture will need to change once we have multiple strategies in the retail app
    strategy_ticker = "CFBG1"

    strategy_latest_weights = backtestsDB.get_strategy_latest_weights(
        database, strategy_ticker)

    target_weights = strategy_latest_weights["weights"]

    result = Binance.rebalance_portfolio(
        api_key=api_key, api_secret=api_secret, account_name=account_name, target_weights=target_weights)

    return json.dumps(result)


# TODO secure this endpoint with e.g. JWT token
@app.route("/persist_all_portfolio_snapshots")
def persist_all_portfolio_snapshots():
    users = coinfolio_get_users()
    binance_persist_all_portfolio_snapshots(database, users)
    return json.dumps({"status": 200})


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

    first_asset_metadata = marketDataDB.get_metadata(
        database, first_asset)
    second_asset_metadata = marketDataDB.get_metadata(
        database, second_asset)

    warnings = series_warnings.get_series_warnings(data["series_df"])

    result = {
        "first_asset": first_asset,
        "second_asset": second_asset,
        "start_date": start_date,
        "end_date": end_date,
        "time_period": time_period_shift,
        "correlation": data["correlation"],
        "series": timeseries_df_to_json(data["series_df"]),
        "first_asset_metadata": first_asset_metadata,
        "second_asset_metadata": second_asset_metadata,
        "warnings": warnings
    }

    json_result = simplejson.dumps(result, ignore_nan=True,
                                   default=datetime.datetime.isoformat)

    return json_result


@app.route("/analytics-tools/performance-compare")
def analytics_tools_performance_compare():

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

    first_asset_metadata = marketDataDB.get_metadata(
        database, first_asset)
    second_asset_metadata = marketDataDB.get_metadata(
        database, second_asset)

    warnings = series_warnings.get_series_warnings(data["series_df"])

    result = {
        "first_asset": first_asset,
        "second_asset": second_asset,
        "start_date": start_date,
        "end_date": end_date,
        "time_period": time_period_shift,
        "correlation": data["correlation"],
        "series": timeseries_df_to_json(data["series_df"]),
        "first_asset_metadata": first_asset_metadata,
        "second_asset_metadata": second_asset_metadata,
        "warnings": warnings
    }

    json_result = simplejson.dumps(result, ignore_nan=True,
                                   default=datetime.datetime.isoformat)

    return json_result


@app.route("/analytics-tools/price-chart")
def analytics_tools_price_chart():

    args = request.args

    # TODO we should return error if these query params are not available!
    ticker = args.get("ticker")
    end_date_iso_string = args.get("endDate")
    time_period_shift = args.get("timePeriod")

    def timeseries_df_to_json(df):
        df["date"] = df.index
        return df.to_json(orient="records")

    end_date = datetime.datetime(
        *time.strptime(end_date_iso_string, "%Y-%m-%dT%H:%M:%S.%f%z")[:6])
    start_date = date_utils.get_shifted_date(end_date, time_period_shift)

    data = analyticsToolsDB.get_price_chart_data(
        database, ticker, start_date=start_date, end_date=end_date)

    series = timeseries_df_to_json(data["series_df"])

    ticker_metadata = marketDataDB.get_metadata(
        database, ticker)

    # warnings = series_warnings.get_series_warnings(data["series_df"])

    result = {
        "ticker": ticker,
        "ticker_metadata": ticker_metadata,
        "start_date": start_date,
        "end_date": end_date,
        "time_period": time_period_shift,
        "series": series,
    }

    json_result = simplejson.dumps(result, ignore_nan=True,
                                   default=datetime.datetime.isoformat)

    return json_result


if __name__ == '__main__':
    app.run()
