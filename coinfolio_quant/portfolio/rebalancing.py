from prettyprinter import pprint
from math import floor


def find_unique(predicate, data):
    filtered_items = list(filter(predicate, data))

    if len(filtered_items) != 1:
        raise Exception(
            "Could not find exactly one match for the predicate.")

    return filtered_items[0]


def find_maximally_one_or_none(predicate, data):
    filtered_items = list(filter(predicate, data))
    if len(filtered_items) == 1:
        return filtered_items[0]
    if len(filtered_items) > 1:
        raise Exception(
            "Found more than one match for the predicate!")
    return None


def find_market_data_item(market_data_list, base_currency, quote_currency="USD"):
    def is_position_market_data_item(
        market_data_item): return market_data_item["baseCurrency"] == base_currency and market_data_item["quoteCurrency"] == quote_currency

    market_data_item = find_unique(
        is_position_market_data_item, market_data_list)

    return market_data_item


test_market_data_list = [
    {"baseCurrency": "BTC", "quoteCurrency": "USD"},
    {"baseCurrency": "BTC", "quoteCurrency": "EUR"},
    {"baseCurrency": "EUR", "quoteCurrency": "USD"}
]

assert(find_market_data_item(test_market_data_list, "BTC")
       == {"baseCurrency": "BTC", "quoteCurrency": "USD"})
assert(find_market_data_item(test_market_data_list, "EUR")
       == {"baseCurrency": "EUR", "quoteCurrency": "USD"})
assert(find_market_data_item(test_market_data_list, "BTC", "EUR")
       == {"baseCurrency": "BTC", "quoteCurrency": "EUR"})


# TODO test
def get_total_positions_value(positions):
    portfolio_value_in_usd = 0
    for position in positions:
        portfolio_value_in_usd = portfolio_value_in_usd + position["usdValue"]
    return portfolio_value_in_usd


test_positions = [{"ticker": "EUR", "usdValue": 10},
                  {"ticker": "USDT", "usdValue": 20}]
assert(get_total_positions_value(test_positions) == 30)


# TODO to be coherent we should have the positins field called "usd_value"
def create_target_position(target_weight_item, portfolio_value_in_usd, market_data_list, quote_currency="USD"):

    it = target_weight_item

    position_value_in_usd = it["weight"] * portfolio_value_in_usd

    base_currency = it["ticker"]
    # quote_currency = "USD"
    instrument_price_in_usd = None

    # if base_currency == quote_currency:
    #     instrument_price_in_usd = 1
    # else:
    def is_position_market_data_item(
        market_data_item): return market_data_item["baseCurrency"] == base_currency and market_data_item["quoteCurrency"] == quote_currency

    relevant_market_data_item = find_unique(
        is_position_market_data_item, market_data_list)

    instrument_price_in_usd = relevant_market_data_item["price"]

    ideal_quantity = position_value_in_usd / instrument_price_in_usd
    lot_size = relevant_market_data_item["minProvideSize"]
    lots_amount = floor(ideal_quantity / lot_size)
    quantity = lot_size * lots_amount

    target_position = {
        "ticker": it["ticker"],
        "weight": it["weight"],
        "usdValue": position_value_in_usd,
        "ideal_quantity": ideal_quantity,
        "lot_size": lot_size,
        "quantity": quantity,
    }

    return target_position


def create_target_positions(target_weights, portfolio_value_in_usd, market_data_list, quote_currency="USD"):
    target_positions = [create_target_position(it,
                                               portfolio_value_in_usd,
                                               market_data_list, quote_currency=quote_currency)
                        for it in target_weights]

    return target_positions


test_target_weights = [{"ticker": "BTC", "weight": 0.4}, {
    "ticker": "ETH", "weight": 0.6}]
test_portfolio_value_in_usd = 1000
test_market_data_list = [
    {"baseCurrency": "BTC", "quoteCurrency": "USD",
        "price": 10, "minProvideSize": 0.01},
    {"baseCurrency": "ETH", "quoteCurrency": "USD",
        "price": 1, "minProvideSize": 0.001},
]

test_target_positions = create_target_positions(
    test_target_weights, test_portfolio_value_in_usd, test_market_data_list)

# TODO test also with minProvideSize integration!
assert(test_target_positions == [
    {
        'ticker': 'BTC',
        'weight': 0.4,
        'usdValue': 400.0,
        'ideal_quantity': 40.0,
        'lot_size': 0.01,
        'quantity': 40.0
    },
    {
        'ticker': 'ETH',
        'weight': 0.6,
        'usdValue': 600.0,
        'ideal_quantity': 600.0,
        'lot_size': 0.001,
        'quantity': 600.0
    }
])


test_target_weights = [{"ticker": "BTC", "weight": 0.4}, {
    "ticker": "ETH", "weight": 0.6}]
test_portfolio_value_in_usd = 800
test_market_data_list = [
    {"baseCurrency": "BTC", "quoteCurrency": "USD",
        "price": 9.83, "minProvideSize": 0.01},
    {"baseCurrency": "ETH", "quoteCurrency": "USD",
        "price": 0.34, "minProvideSize": 0.001},
]

test_target_positions = create_target_positions(
    test_target_weights, test_portfolio_value_in_usd, test_market_data_list)

assert(test_target_positions ==
       [{'ticker': 'BTC',
         'weight': 0.4,
         'usdValue': 320.0,
         'ideal_quantity': 32.55340793489319,
         'lot_size': 0.01,
         'quantity': 32.55},
        {'ticker': 'ETH',
           'weight': 0.6,
           'usdValue': 480.0,
           'ideal_quantity': 1411.764705882353,
           'lot_size': 0.001,
           'quantity': 1411.7640000000001}]
       )


def create_liquidation(current_position, target_positions):
    position_ticker = current_position["ticker"]
    target_position = find_maximally_one_or_none(
        lambda p: p["ticker"] == position_ticker, target_positions)

    # if target position
    if target_position:
        # if target position smaller, liquidate the difference
        if current_position["quantity"] > target_position["quantity"]:
            return {"ticker": position_ticker, "liquidation_quantity": current_position["quantity"] - target_position["quantity"]}
        # if target position larger, liquidate 0
        else:
            return {"ticker": position_ticker, "liquidation_quantity": 0}

    # if no target position, liquidate all

    return {
        "ticker": position_ticker, "liquidation_quantity": current_position["quantity"]
    }


test_current_position = {"ticker": "AAA", "quantity": 100}
test_target_positions = [{"ticker": "AAA", "quantity": 10}, {
    "ticker": "BBB", "quantity": 50}]
assert(create_liquidation(test_current_position, test_target_positions)
       == {"ticker": "AAA", "liquidation_quantity": 90})


def create_liquidations(current_positions, target_positions, account_currency="USD"):
    all_liquidations = [create_liquidation(
        current_position, target_positions) for current_position in current_positions]

    positive_liquidations = list(
        filter(lambda it: it["liquidation_quantity"] > 0, all_liquidations))
    non_usd_liquidations = list(
        filter(lambda it: it["ticker"] != account_currency, positive_liquidations))

    return non_usd_liquidations


def create_rebalancing_buys(target_positions, current_positions, market_data_list, quote_currency="USD"):
    # print("in rebalancing buys::::::::::::::")
    # print("target_positions")
    # print(target_positions)
    # print("current_positions")
    # print(current_positions)
    # print("market_data_list")
    # print(market_data_list)
    # print("==========================")
    rebalancing_buys = []
    for target_position in target_positions:
        ticker = target_position["ticker"]
        matching_current_position = find_maximally_one_or_none(
            lambda p: p["ticker"] == ticker, current_positions)

        ideal_buy_quantity = target_position["quantity"]
        if matching_current_position:
            ideal_buy_quantity = ideal_buy_quantity - \
                matching_current_position["quantity"]

        market_data_item = find_market_data_item(
            market_data_list, ticker, quote_currency=quote_currency)

        lot_size = market_data_item["minProvideSize"]
        lots_amount = floor(ideal_buy_quantity / lot_size)
        buy_quantity = lot_size * lots_amount

        rebalancing_buys.append({"ticker": ticker, "buy_quantity": buy_quantity,
                                "ideal_buy_quantity": ideal_buy_quantity})

    return rebalancing_buys
