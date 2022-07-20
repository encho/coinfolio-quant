import yfinance as yf
import progressbar


def get_bitcoin_only_universe(date):
    return ["BTC"]


def get_g4_universe(date):
    return ["BTC", "ETH", "XRP", "ADA"]


def get_g2_universe(date):
    return ["BTC", "ETH"]


def get_gold_crypto_universe(date):
    return ["XAU", "BTC"]


def get_coinfolio_gold_crypto_universe(date):
    return ["XAU", "BTC", "ETH", "XRP", "ADA"]


def get_equally_weighted_asset_allocation(date, universe):
    currencies_amount = len(universe)
    return [{"ticker": ticker, "weight": 1/currencies_amount} for ticker in universe]


def get_60_40_asset_allocation(date, universe):
    return [{"ticker": universe[0], "weight": 0.6}, {"ticker": universe[1], "weight": 0.4}]


def get_70_30_asset_allocation(date, universe):
    return [{"ticker": universe[0], "weight": 0.7}, {"ticker": universe[1], "weight": 0.3}]


def get_coinfolio_gold_crypto_asset_allocation(date, universe):
    return [{"ticker": ticker, "weight": 0.6 if ticker == "XAU" else 0.4/4} for ticker in universe]


def get_single_long_only_asset_allocation(date, universe):
    # TODO throw error if universe longer than 1
    return [{"ticker": universe[0], "weight": 1}]


STRATEGIES_SPECS = [
    # {
    #     "ticker": "G4_EQUALLY_WEIGHTED",
    #     "get_universe": get_g4_universe,
    #     "get_weights": get_equally_weighted_asset_allocation
    # },
    # {
    #     "ticker": "G2_EQUALLY_WEIGHTED",
    #     "get_universe": get_g2_universe,
    #     "get_weights": get_equally_weighted_asset_allocation
    # },
    # {
    #     "ticker": "GOLD_CRYPTO_50_50",
    #     "get_universe": get_gold_crypto_universe,
    #     "get_weights": get_equally_weighted_asset_allocation
    # },
    {
        "ticker": "BITCOIN_ONLY",
        "get_universe": get_bitcoin_only_universe,
        "get_weights": get_single_long_only_asset_allocation
    },
    {
        "ticker": "GOLD_CRYPTO_60_40",
        "get_universe": get_gold_crypto_universe,
        "get_weights": get_60_40_asset_allocation
    },
    # {
    #     "ticker": "GOLD_CRYPTO_70_30",
    #     "get_universe": get_gold_crypto_universe,
    #     "get_weights": get_70_30_asset_allocation
    # },
    # {
    #     "ticker": "COINFOLIO_GOLD_CRYPTO",
    #     "get_universe": get_coinfolio_gold_crypto_universe,
    #     "get_weights": get_coinfolio_gold_crypto_asset_allocation
    # }
]


def create_strategy_weights(strategy_weights_collection, strategy_ticker, date):
    strategy_specs = list(filter(
        lambda it: it["ticker"] == strategy_ticker,
        STRATEGIES_SPECS
    ))
    if len(strategy_specs) != 1:
        raise Exception(
            "Either no STRATEGY_SPEC or too many for: " + strategy_ticker)
    strategy_spec = strategy_specs[0]

    currency_universe = strategy_spec["get_universe"](date)

    strategy_weights = strategy_spec["get_weights"](
        date, currency_universe)

    strategy_weights_record = {
        "ticker": strategy_ticker,
        "date": date,
        "weights": strategy_weights
    }

    strategy_weights_collection.insert_one(strategy_weights_record)
