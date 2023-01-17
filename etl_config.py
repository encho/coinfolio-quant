import datetime
import etl_utils_strategy_weights_allocation as assetAllocation
import etl_utils_strategy_weights_universe as universe

RESET_START_DATE = datetime.date(2014, 9, 17)
RESET_END_DATE = datetime.date.today() - datetime.timedelta(days=1)

UPDATE_START_DATE = datetime.date.today() - datetime.timedelta(days=7)
UPDATE_END_DATE = datetime.date.today() - datetime.timedelta(days=1)

# TODO differentiate between exchange rates/ prices/ indices....?
MARKET_DATA_METADATA = [
    {"ticker": "BTC-USD", "base": "BTC", "quote": "USD",
        "yahoo_ticker": "BTC-USD", "name": "Bitcoin/USD", "type": "CRYPTO", "version": 1},
    {"ticker": "XAU-USD", "base": "XAU", "quote": "USD",
        "yahoo_ticker": "GC=F", "name": "Gold/USD", "type": "COMMODITY", "version": 1},
    {"ticker": "^DJCI", "base": "DJCI", "quote": "USD",
        "yahoo_ticker": "^DJCI", "name": "DJ Commodity Index", "type": "COMMODITY", "version": 2},
    {"ticker": "ETH-USD", "base": "ETH", "quote": "USD",
        "yahoo_ticker": "ETH-USD", "name": "Ethereum/USD", "type": "CRYPTO", "version": 1},
    {"ticker": "XRP-USD", "base": "XRP", "quote": "USD",
        "yahoo_ticker": "XRP-USD", "name": "Ripple/USD", "type": "CRYPTO", "version": 1},
    {"ticker": "ADA-USD", "base": "ADA", "quote": "USD",
        "yahoo_ticker": "ADA-USD", "name": "Cardano/USD", "type": "CRYPTO", "version": 1},
    {"ticker": "GBP-USD", "base": "GBP", "quote": "USD",
        "yahoo_ticker": "GBPUSD=X", "name": "British Pound/USD", "type": "FX", "version": 1},
    {"ticker": "EUR-USD", "base": "EUR", "quote": "USD",
        "yahoo_ticker": "EURUSD=X", "name": "Euro/USD", "type": "FX", "version": 1},
    {"ticker": "JPY-USD", "base": "JPY", "quote": "USD",
        "yahoo_ticker": "JPYUSD=X", "name": "Japan Yen/USD", "type": "FX", "version": 1},
    {"ticker": "AUD-USD", "base": "AUD", "quote": "USD",
        "yahoo_ticker": "AUDUSD=X", "name": "AUD/USD", "type": "FX", "version": 2},
    {"ticker": "NZD-USD", "base": "NZD", "quote": "USD",
        "yahoo_ticker": "NZDUSD=X", "name": "NZD/USD", "type": "FX", "version": 2},
    {"ticker": "EUR-CHF", "base": "EUR", "quote": "CHF",
        "yahoo_ticker": "EURCHF=X", "name": "EUR/CHF", "type": "FX", "version": 2},
    {"ticker": "USD-RUB", "base": "USD", "quote": "RUB",
        "yahoo_ticker": "RUB=X", "name": "USD/RUB", "type": "FX", "version": 2},
    {"ticker": "FTSE_INDEX", "base": "FTSE",
        "quote": "GBP", "yahoo_ticker": "^FTSE", "name": "FTSE Index", "type": "STOCK_INDEX", "version": 1},
    {"ticker": "DAX_INDEX", "base": "DAX", "quote": "EUR",
        "yahoo_ticker": "^GDAXI", "name": "DAX Index", "type": "STOCK_INDEX", "version": 1},
    {"ticker": "^N100", "base": "^N100", "quote": "EUR",
        "yahoo_ticker": "^N100", "name": "Euronext 100", "type": "STOCK_INDEX", "version": 2},
    {"ticker": "SPX_INDEX", "base": "S&P", "quote": "USD",
        "yahoo_ticker": "^GSPC", "name": "S&P Index", "type": "STOCK_INDEX", "version": 1},
    {"ticker": "DJI_INDEX", "base": "DJI", "quote": "USD",
        "yahoo_ticker": "^DJI", "name": "Dow Jones Index", "type": "STOCK_INDEX", "version": 2},
    {"ticker": "NIKKEI_INDEX", "base": "NIKKEI225",
        "quote": "USD", "yahoo_ticker": "^N225", "name": "Nikkei Index", "type": "FX", "version": 1},
    {"ticker": "AAPL", "base": "AAPL", "quote": "USD",
        "yahoo_ticker": "AAPL", "name": "Apple", "type": "STOCK", "version": 2},
    {"ticker": "AMZN", "base": "AMZN", "quote": "USD",
        "yahoo_ticker": "AMZN", "name": "Amazon.com", "type": "STOCK", "version": 2},
    {"ticker": "COIN", "base": "COIN", "quote": "USD",
        "yahoo_ticker": "COIN", "name": "Coinbase Global", "type": "STOCK", "version": 2},
    {"ticker": "PFE", "base": "PFE", "quote": "USD",
        "yahoo_ticker": "PFE", "name": "Pfizer", "type": "STOCK", "version": 2},
    {"ticker": "GS", "base": "GS", "quote": "USD",
        "yahoo_ticker": "GS", "name": "Goldman Sachs", "type": "STOCK", "version": 2},
    {"ticker": "JPM", "base": "JPM", "quote": "USD",
        "yahoo_ticker": "JPM", "name": "JPMorgan Chase", "type": "STOCK", "version": 2},
    {"ticker": "TESLA", "base": "TESLA", "quote": "USD",
        "yahoo_ticker": "TSLA", "name": "Tesla Stock", "type": "STOCK", "version": 1},
]


STRATEGIES_SPECS = [
    {
        "ticker": "BITCOIN_ONLY",
        "name": "Bitcoin Long Only Strategy",
        "description": "Bitcoin Long Only Strategy Description",
        "rebalancing": "DAILY",
        "get_universe": universe.get_bitcoin_only_universe,
        "get_weights": assetAllocation.get_single_long_only_asset_allocation,
    },
    {
        "ticker": "GOLD_ONLY",
        "name": "Gold Long Only Strategy",
        "description": "Gold Long Only Strategy Description",
        "rebalancing": "MONTHLY",
        "get_universe": universe.get_gold_only_universe,
        "get_weights": assetAllocation.get_single_long_only_asset_allocation,
    },
    {
        "ticker": "CFBG1",
        "name": "Coinfolio Bitcoin & Gold Balanced Index",
        "description": "Coinfolio Bitcoin & Gold Balanced Index (Description)",
        "rebalancing": "MONTHLY",
        "get_universe": universe.get_gold_crypto_universe,
        "get_weights": assetAllocation.make_inv_vola_aa(360)
    },
    {
        "ticker": "GOLD_CRYPTO_60_40",
        "name": "Gold Crypto 60-40 Basket",
        "description": "Gold & Crypto Portfolio 60/40",
        "rebalancing": "MONTHLY",
        "get_universe": universe.get_gold_crypto_universe,
        "get_weights": assetAllocation.get_60_40_asset_allocation,
    },
]
