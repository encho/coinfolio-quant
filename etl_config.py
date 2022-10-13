import datetime

START_DATE = datetime.date(2014, 9, 17)
END_DATE = datetime.date.today() - datetime.timedelta(days=1)


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
