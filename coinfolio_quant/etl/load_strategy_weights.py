import yfinance as yf
import progressbar


def get_g4_universe(date):
    return ["BTC", "ETH", "XRP", "ADA"]


def get_g2_universe(date):
    return ["BTC", "ETH"]


def get_equally_weighted_asset_allocation(date, universe):
    currencies_amount = len(universe)
    return [{"ticker": ticker, "weight": 1/currencies_amount} for ticker in universe]


STRATEGIES_SPECS = [
    {
        "ticker": "G4_EQUALLY_WEIGHTED",
        "get_universe": get_g4_universe,
        "get_weights": get_equally_weighted_asset_allocation
    },
    {
        "ticker": "G2_EQUALLY_WEIGHTED",
        "get_universe": get_g2_universe,
        "get_weights": get_equally_weighted_asset_allocation
    }
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

    print("computing strategy weights strategy: " +
          strategy_ticker + ", date: " + date.strftime("%Y-%m-%d, %H:%M:%S"))

    print("currency universe:")
    print(currency_universe)

    strategy_weights = strategy_spec["get_weights"](
        date, currency_universe)

    print("strategy weights:")
    print(strategy_weights)

    strategy_weights_record = {
        "ticker": strategy_ticker,
        "date": date,
        "weights": strategy_weights
    }

    print("strategy weights record:")
    print(strategy_weights_record)

    strategy_weights_collection.insert_one(strategy_weights_record)
