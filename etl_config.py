import datetime
import etl_utils_strategy_weights_allocation as assetAllocation
import etl_utils_strategy_weights_universe as universe

RESET_START_DATE = datetime.date(2014, 9, 17)
RESET_END_DATE = datetime.date.today() - datetime.timedelta(days=1)
# RESET_START_DATE = datetime.date(2020, 9, 17)
# RESET_END_DATE = datetime.date(2022, 9, 17)

UPDATE_START_DATE = datetime.date.today() - datetime.timedelta(days=7)
UPDATE_END_DATE = datetime.date.today() - datetime.timedelta(days=1)

MARKET_DATA_METADATA = [
    {"ticker": "BTC-USD", "base": "BTC", "quote": "USD",
        "yahoo_ticker": "BTC-USD", "name": "Bitcoin/USD", "type": "CRYPTO", "price_format_string": "$0,0","version": 1},
    {"ticker": "XAU-USD", "base": "XAU", "quote": "USD",
        "yahoo_ticker": "GC=F", "name": "Gold/USD", "type": "COMMODITY", "price_format_string": "$0,0","version": 1},
    {"ticker": "ETH-USD", "base": "ETH", "quote": "USD",
        "yahoo_ticker": "ETH-USD", "name": "Ethereum/USD", "type": "CRYPTO", "price_format_string": "$0,0","version": 1},
    {"ticker": "XRP-USD", "base": "XRP", "quote": "USD",
        "yahoo_ticker": "XRP-USD", "name": "Ripple/USD", "type": "CRYPTO", "price_format_string": "$0,0", "version": 1},
    {"ticker": "USDT-USD", "base": "USDT", "quote": "USD",
        "yahoo_ticker": "USDT-USD", "name": "Tether/USD", "type": "CRYPTO", "price_format_string": "$0,0", "version": 2},
    {"ticker": "BNB-USD", "base": "BNB", "quote": "USD",
        "yahoo_ticker": "BNB-USD", "name": "BNB/USD", "type": "CRYPTO", "price_format_string": "$0,0", "version": 2},
    {"ticker": "ADA-USD", "base": "ADA", "quote": "USD",
        "yahoo_ticker": "ADA-USD", "name": "Cardano/USD", "type": "CRYPTO", "price_format_string": "$0,0", "version": 1},
    {"ticker": "GBP-USD", "base": "GBP", "quote": "USD",
        "yahoo_ticker": "GBPUSD=X", "name": "GBP/USD", "type": "FX", "price_format_string": "$0,0", "version": 1},
    {"ticker": "EUR-USD", "base": "EUR", "quote": "USD",
        "yahoo_ticker": "EURUSD=X", "name": "EUR/USD", "type": "FX", "price_format_string": "$0,0", "version": 1},
    {"ticker": "JPY-USD", "base": "JPY", "quote": "USD",
        "yahoo_ticker": "JPYUSD=X", "name": "JPY/USD", "type": "FX", "price_format_string": "0,0000", "version": 1},
    {"ticker": "AUD-USD", "base": "AUD", "quote": "USD",
        "yahoo_ticker": "AUDUSD=X", "name": "AUD/USD", "type": "FX", "price_format_string": "0,0", "version": 2},
    {"ticker": "NZD-USD", "base": "NZD", "quote": "USD",
        "yahoo_ticker": "NZDUSD=X", "name": "NZD/USD", "type": "FX", "price_format_string": "0,0", "version": 2},
    {"ticker": "EUR-CHF", "base": "EUR", "quote": "CHF",
        "yahoo_ticker": "EURCHF=X", "name": "EUR/CHF", "type": "FX", "price_format_string": "0,0", "version": 2},
    {"ticker": "USD-RUB", "base": "USD", "quote": "RUB",
        "yahoo_ticker": "RUB=X", "name": "USD/RUB", "type": "FX", "price_format_string": "0,0", "version": 2},
    {"ticker": "FTSE_INDEX", "base": "FTSE",
        "quote": "GBP", "yahoo_ticker": "^FTSE", "name": "FTSE Index", "type": "STOCK_INDEX", "price_format_string": "0,0", "version": 1},
    {"ticker": "DAX_INDEX", "base": "DAX", "quote": "EUR",
        "yahoo_ticker": "^GDAXI", "name": "DAX Index", "type": "STOCK_INDEX", "price_format_string": "0,0", "version": 1},
    {"ticker": "^N100", "base": "^N100", "quote": "EUR",
        "yahoo_ticker": "^N100", "name": "Euronext 100 Index", "type": "STOCK_INDEX", "price_format_string": "0,0", "version": 2},
    {"ticker": "SPX_INDEX", "base": "S&P", "quote": "USD",
        "yahoo_ticker": "^GSPC", "name": "S&P Index", "type": "STOCK_INDEX", "price_format_string": "0,0","version": 1},
    {"ticker": "DJI_INDEX", "base": "DJI", "quote": "USD",
        "yahoo_ticker": "^DJI", "name": "Dow Jones Index", "type": "STOCK_INDEX", "price_format_string": "0,0", "version": 2},
    {"ticker": "NIKKEI_INDEX", "base": "NIKKEI225",
        "quote": "USD", "yahoo_ticker": "^N225", "name": "Nikkei Index", "type": "STOCK_INDEX", "price_format_string": "0,0", "version": 1},
    {"ticker": "AAPL", "base": "AAPL", "quote": "USD",
        "yahoo_ticker": "AAPL", "name": "Apple", "type": "STOCK", "price_format_string": "0,0", "version": 2},
    {"ticker": "AMZN", "base": "AMZN", "quote": "USD",
        "yahoo_ticker": "AMZN", "name": "Amazon", "type": "STOCK", "price_format_string": "$0,0", "version": 2},
    {"ticker": "COIN", "base": "COIN", "quote": "USD",
        "yahoo_ticker": "COIN", "name": "Coinbase", "type": "STOCK", "price_format_string": "$0,0", "version": 2},
    {"ticker": "PFE", "base": "PFE", "quote": "USD",
        "yahoo_ticker": "PFE", "name": "Pfizer", "type": "STOCK", "price_format_string": "$0,0", "version": 2},
    {"ticker": "GS", "base": "GS", "quote": "USD",
        "yahoo_ticker": "GS", "name": "Goldman Sachs", "type": "STOCK", "price_format_string": "$0,0", "version": 2},
    {"ticker": "JPM", "base": "JPM", "quote": "USD",
        "yahoo_ticker": "JPM", "name": "JPMorgan Chase", "type": "STOCK", "price_format_string": "$0,0", "version": 2},
    {"ticker": "TESLA", "base": "TESLA", "quote": "USD",
        "yahoo_ticker": "TSLA", "name": "Tesla", "type": "STOCK", "price_format_string": "$0,0", "version": 1},
]

# TODO add startDate for the backtests
# TODO add currency option
STRATEGIES_SPECS = [
    {
        "ticker": "BITCOIN_ONLY",
        "name": "Bitcoin Long Only Strategy",
        "description": "Captures long-term Bitcoin growth by employing a simple buy-and-hold approach, focusing on its potential as a high-growth asset.",
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
        "ticker": "BITCOIN_GOLD_VOLA_BALANCED_360",
        "name": "Bitcoin & Gold Balanced Index",
        "description": "Adjusting portfolio weights to equalize risk by inversely scaling gold and bitcoin allocations to their 360-day volatility.",
        "rebalancing": "MONTHLY",
        "get_universe": universe.get_gold_crypto_universe,
        "get_weights": assetAllocation.make_inv_vola_aa(360)
    },
    {
        "ticker": "GOLD_CRYPTO_80_20",
        "name": "Gold & Crypto 80/20 Portfolio",
        "description": "Maintains a balanced allocation in Gold (80%) and Bitcoin (20%), combining stability and growth potential for long-term wealth preservation.",
        "rebalancing": "MONTHLY",
        "get_universe": universe.get_gold_crypto_universe,
        "get_weights": assetAllocation.get_2_assets_fixed_weights_asset_allocation_fun(0.8,0.2),
    },
    {
        "ticker": "GOLD_CRYPTO_60_40",
        "name": "Gold & Crypto 60/40 Portfolio",
        "description": "Maintains a balanced allocation in Gold (60%) and Bitcoin (40%), combining stability and growth potential for long-term wealth preservation.",
        "rebalancing": "MONTHLY",
        "get_universe": universe.get_gold_crypto_universe,
        "get_weights": assetAllocation.get_60_40_asset_allocation,
    },
]
