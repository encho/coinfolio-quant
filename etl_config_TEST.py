import datetime
import etl_utils_strategy_weights_allocation as assetAllocation
import etl_utils_strategy_weights_universe as universe

RESET_START_DATE = datetime.date.today() - datetime.timedelta(days=30)
RESET_END_DATE = datetime.date.today() - datetime.timedelta(days=10)


UPDATE_START_DATE = datetime.date.today() - datetime.timedelta(days=10)
UPDATE_END_DATE = datetime.date.today() - datetime.timedelta(days=1)


# TODO differentiate between exchange rates/ prices/ indices....?
MARKET_DATA_METADATA = [
    {"ticker": "BTC-USD", "base": "BTC", "quote": "USD",
        "yahoo_ticker": "BTC-USD", "name": "Bitcoin/USD", "type": "CRYPTO"},
    {"ticker": "XAU-USD", "base": "XAU", "quote": "USD",
        "yahoo_ticker": "GC=F", "name": "Gold/USD", "type": "COMMODITY"},
    {"ticker": "ETH-USD", "base": "ETH", "quote": "USD",
        "yahoo_ticker": "ETH-USD", "name": "Ethereum/USD", "type": "CRYPTO"},
    {"ticker": "XRP-USD", "base": "XRP", "quote": "USD",
        "yahoo_ticker": "XRP-USD", "name": "Ripple/USD", "type": "CRYPTO"},
    {"ticker": "ADA-USD", "base": "ADA", "quote": "USD",
        "yahoo_ticker": "ADA-USD", "name": "Cardano/USD", "type": "CRYPTO"},
    {"ticker": "GBP-USD", "base": "GBP", "quote": "USD",
        "yahoo_ticker": "GBPUSD=X", "name": "British Pound/USD", "type": "FX"},
    {"ticker": "EUR-USD", "base": "EUR", "quote": "USD",
        "yahoo_ticker": "EURUSD=X", "name": "Euro/USD", "type": "FX"},
    {"ticker": "JPY-USD", "base": "JPY", "quote": "USD",
        "yahoo_ticker": "JPYUSD=X", "name": "Japan Yen/USD", "type": "FX"},
    {"ticker": "FTSE_INDEX", "base": "FTSE",
        "quote": "GBP", "yahoo_ticker": "^FTSE", "name": "FTSE Index", "type": "FX"},
    {"ticker": "DAX_INDEX", "base": "DAX", "quote": "EUR",
        "yahoo_ticker": "^GDAXI", "name": "DAX Index", "type": "FX"},
    {"ticker": "SPX_INDEX", "base": "S&P", "quote": "USD",
        "yahoo_ticker": "^GSPC", "name": "S&P Index", "type": "FX"},
    {"ticker": "NIKKEI_INDEX", "base": "NIKKEI225",
        "quote": "USD", "yahoo_ticker": "^N225", "name": "Nikkei Index", "type": "FX"},
    {"ticker": "TESLA", "base": "TESLA", "quote": "USD",
        "yahoo_ticker": "TSLA", "name": "Tesla Stock", "type": "FX"},
]


STRATEGIES_SPECS = [
    {
        "ticker": "BITCOIN_ONLY",
        "name": "Bitcoin Long Only Strategy",
        "description": "Bitcoin Long Only Strategy Description",
        "rebalancing": "DAILY",
        # TODO make data-based
        "get_universe": universe.get_bitcoin_only_universe,
        "get_weights": assetAllocation.get_single_long_only_asset_allocation,
    },
    {
        "ticker": "CFBG1",
        "name": "Coinfolio Bitcoin & Gold Balanced Index",
        "description": "Coinfolio Bitcoin & Gold Balanced Index (Description)",
        "rebalancing": "MONTHLY",
        # TODO make data-based
        "get_universe": universe.get_gold_crypto_universe,
        # TODO make data-based
        # e.g: ["inverted_vola", 360]
        "get_weights": assetAllocation.make_inv_vola_aa(10)
    },
    # {
    #     "ticker": "GOLD_CRYPTO_60_40",
    #     "name": "Gold Crypto 60-40 Basket",
    #     "description": "Gold & Crypto Portfolio 60/40",
    #     "rebalancing": "MONTHLY",
    #     # TODO make data-based
    #     "get_universe": universe.get_gold_crypto_universe,
    #     "get_weights": assetAllocation.get_60_40_asset_allocation,
    # },
]
