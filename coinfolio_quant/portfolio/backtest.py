import copy
import numpy as np
from prettyprinter import pprint

# TODO eventually into utils


def find_unique(predicate, data):
    filtered_items = list(filter(predicate, data))

    if len(filtered_items) != 1:
        raise Exception(
            "Could not find exaclty one match for the predicate.")

    return filtered_items[0]


# TODO eventually into utils
def get_field_value(field, check_field, check_value, data_list, default_value):
    def predicate(it): return it[check_field] == check_value
    filtered_items = list(filter(predicate, data_list))

    if len(filtered_items) > 1:
        raise Exception(
            "Too many matches for the predicate.")
    if len(filtered_items) < 1:
        return default_value
    else:
        return filtered_items[0][field]


def get_position_market_value(position, currency, prices):
    exchange_rate_ticker = position["ticker"]+"-"+currency
    price = prices[exchange_rate_ticker]
    quantity = position["quantity"]
    market_value = price * quantity
    return market_value


# unit test
test_position = {"ticker": "BTC", "quantity": 10}
test_currency = "USD"
test_prices = {"BTC-USD": 2}
assert(get_position_market_value(test_position, test_currency, test_prices) == 20)


def get_positions_market_value(positions, currency, prices):
    positions_values = [get_position_market_value(
        position, currency, prices) for position in positions]
    return sum(positions_values)


# unit test
test_positions = [{"ticker": "BTC", "quantity": 1},
                  {"ticker": "ETH", "quantity": 10}]
test_prices = {"BTC-USD": 1, "ETH-USD": 1}
test_positions_value = get_positions_market_value(
    test_positions, "USD", test_prices)
assert(test_positions_value == 11)


def get_portfolio_market_value(portfolio, prices):
    positions_market_value = get_positions_market_value(
        portfolio["positions"], portfolio["currency"], prices)
    return portfolio["cash"] + positions_market_value


# unit test
test_portfolio = {
    "currency": "USD",
    "cash": 10,
    "transactions": [],
    "positions": [{"ticker": "BTC", "quantity": 1},
                  {"ticker": "ETH", "quantity": 10}]
}
test_prices = {"BTC-USD": 1, "ETH-USD": 1}
test_portfolio_value = get_portfolio_market_value(
    test_portfolio, test_prices)
assert(test_portfolio_value == 21)


def get_set_of_tickers(positions, weights):
    positions_tickers = [position["ticker"] for position in positions]
    weights_tickers = [weight["ticker"] for weight in weights]
    return set(positions_tickers + weights_tickers)


# unit test
test_positions = [{"ticker": "BTC", "quantity": 1},
                  {"ticker": "ETH", "quantity": 10}]
test_weights = [{"ticker": "XRP", "weight": 0.25}]
assert(get_set_of_tickers(test_positions, test_weights)
       == {"BTC", "XRP", "ETH"})


def get_position_quantity(positions, ticker):
    return get_field_value("quantity", "ticker", ticker, positions, 0)


# unit test
test_positions = [{"ticker": "BTC", "quantity": 1},
                  {"ticker": "ETH", "quantity": 10}]
assert(get_position_quantity(test_positions, "ETH") == 10)
assert(get_position_quantity(test_positions, "NOT_THERE") == 0)


def get_weight(weights, ticker):
    return get_field_value("weight", "ticker", ticker, weights, 0)


# unit test
test_weights = [{"ticker": "BTC", "weight": 0.25},
                {"ticker": "ETH", "weight": 0.75}]
assert(get_weight(test_weights, "BTC") == 0.25)
assert(get_weight(test_weights, "ETH") == 0.75)
assert(get_weight(test_weights, "XRP") == 0)


def create_rebalancing_item(ticker, positions, weights, prices, portfolio_value, currency):

    old_quantity = get_position_quantity(positions, ticker)
    price = prices[ticker+"-"+currency]
    old_value = old_quantity * price

    new_weight = get_weight(weights, ticker)
    new_value = new_weight * portfolio_value

    item = {
        "ticker": ticker,
        "old_quantity": old_quantity,
        "old_value": old_value,
        "new_weight": new_weight,
        "new_value": new_value,
        "transaction_value": new_value - old_value,
        "price": price
    }

    return item


def create_rebalancing_list(portfolio, weights, prices):
    positions = portfolio["positions"]
    currency = portfolio["currency"]

    list_of_tickers = list(get_set_of_tickers(positions, weights))

    current_portfolio_market_value = get_portfolio_market_value(
        portfolio, prices)

    rebalancing_list = [
        create_rebalancing_item(
            ticker=ticker,
            positions=positions,
            weights=weights,
            prices=prices,
            portfolio_value=current_portfolio_market_value,
            currency=currency
        ) for ticker in list_of_tickers]

    return rebalancing_list


def create_transactions(rebalancing_list, date, commission=0):
    perc_transactions_costs = commission
    transactions = []
    non_zero_rebalancings = filter(
        lambda rebalancing_item: rebalancing_item["transaction_value"] != 0, rebalancing_list)
    for rebalancing_item in non_zero_rebalancings:
        ticker = rebalancing_item["ticker"]
        price = rebalancing_item["price"]
        transaction_value = rebalancing_item["transaction_value"]
        side = "BUY" if transaction_value > 0 else "SELL"

        commission_value = abs(transaction_value * perc_transactions_costs)

        net_transaction_value = abs(transaction_value)

        transactions.append({
            "type": "TRADE",
            "ticker": ticker,
            "date": date,
            "value": net_transaction_value,
            "quantity": net_transaction_value / price,
            "side": side,
            "price": price
        })

        transactions.append({
            "type": "COMMISSION",
            "date": date,
            "value": commission_value,
        })
    return transactions


def get_transactions_cash_flow(transactions):
    cash_flow = 0
    for transaction in transactions:
        transaction_type = transaction["type"]
        transaction_value = transaction["value"]

        if transaction_type == "TRADE":
            transaction_side = transaction["side"]
            if transaction_side == "BUY":
                cash_flow = cash_flow - transaction_value
            elif transaction_side == "SELL":
                cash_flow = cash_flow + transaction_value
        elif transaction_type == "COMMISSION":
            cash_flow = cash_flow - transaction_value

    return cash_flow


test_transactions = [{"type": "TRADE", "side": "BUY", "value": 100}, {
    "type": "TRADE", "side": "SELL", "value": 50}, {"type": "COMMISSION", "value": 10}]
assert(get_transactions_cash_flow(test_transactions) == -60)


def get_transactions_commissions(transactions):
    commissions = 0
    for transaction in transactions:
        transaction_type = transaction["type"]
        transaction_value = transaction["value"]

        if transaction_type == "COMMISSION":
            commissions = commissions + transaction_value

    return commissions


test_transactions = [{"type": "COMMISSION", "value": 45}, {"type": "TRADE", "side": "BUY", "value": 100}, {
    "type": "TRADE", "side": "SELL", "value": 50}, {"type": "COMMISSION", "value": 10}]
assert(get_transactions_commissions(test_transactions) == 55)


def has_ticker(positions, ticker):
    return any(map(lambda p: p["ticker"] == ticker, positions))


test_positions = [{"ticker": "BTC"}, {"ticker": "ETH"}]
test_has_positon = has_ticker(test_positions, "ETH")
assert(test_has_positon == True)

test_positions = [{"ticker": "BTC"}, {"ticker": "ETH"}]
test_has_positon = has_ticker(test_positions, "ZZZ")
assert(test_has_positon == False)


def calculate_average_price(position, transaction):
    if transaction["side"] == "BUY":
        position_expenditure = position["average_price"] * position["quantity"]
        transaction_expenditure = transaction["quantity"] * \
            transaction["price"]
        total_expenditure = position_expenditure + transaction_expenditure
        average_price = total_expenditure / \
            (position["quantity"] + transaction["quantity"])
        return average_price
    else:
        return position["average_price"]


def maybe_update_position(position, transaction):
    if position["ticker"] != transaction["ticker"]:
        return position
    else:
        quantity_multiplier = 1 if transaction["side"] == "BUY" else -1
        return {
            "ticker": position["ticker"],
            "quantity": position["quantity"] + transaction["quantity"] * quantity_multiplier,
            "average_price": calculate_average_price(position, transaction)
        }


def update_positions(positions, transactions):
    updated_positions = copy.deepcopy(positions)
    for transaction in transactions:
        if transaction["type"] == "TRADE":
            has_ticker_already = has_ticker(
                updated_positions, transaction["ticker"])
            if not has_ticker_already:
                updated_positions.append({
                    "ticker": transaction["ticker"],
                    "quantity": transaction["quantity"],
                    "average_price": transaction["price"]
                })
            else:
                updated_positions = list(map(lambda position: maybe_update_position(
                    position, transaction), updated_positions))

    only_positions_greater_zero = list(filter(
        lambda position: position["quantity"] > 0, updated_positions))

    return only_positions_greater_zero


def update_positions_values_and_weights(positions, prices):
    currency = "USD"

    for position in positions:
        price = prices[position["ticker"]+"-"+currency]
        position["value"] = price * position["quantity"]

    total_value = sum(position["value"] for position in positions)
    for position in positions:
        position["weight"] = position["value"] / total_value

    positions = sorted(positions, key=lambda position: position["weight"])

    return positions


def get_should_rebalance_DAILY(date, last_rebalance_date):
    return date > last_rebalance_date


def get_should_rebalance_MONTHLY(date, last_rebalance_date):
    larger_date = date > last_rebalance_date
    different_month = date.month != last_rebalance_date.month
    return larger_date and different_month


def get_should_rebalance(rebalancing, date, last_rebalance_date):
    if last_rebalance_date == None:
        return True
    if rebalancing == "DAILY":
        return get_should_rebalance_DAILY(date, last_rebalance_date)
    if rebalancing == "MONTHLY":
        return get_should_rebalance_MONTHLY(date, last_rebalance_date)


def create_next_portfolio(portfolio, weights, prices, date, strategy_info):

    # we always ffill prices which are passed here, i.e. we have a price for
    # each day EXCEPT at the very start of the backtest, where we may not be able
    # to successfully ffill (e.g. if we start the backtest on a saturday with no gold prices)
    # THUS: if we happen to not have a price it has to be at the start of the backtest and in that
    # case we will return the original start portfolio with the current date
    can_not_create_next_portfolio = any(
        np.isnan(price) for price in prices.values())

    # check if for some edge case scenario weights are na's and replace them with zero
    amended_weights = []
    for weight in weights:
        amended_weights.append(
            {"ticker": weight["ticker"], "weight": weight["weight"] if not np.isnan(weight["weight"]) else 0})
    weights = amended_weights
    weights = sorted(weights, key=lambda weight: weight["weight"])

    if can_not_create_next_portfolio:
        next_portfolio = portfolio.copy()
        next_portfolio["date"] = date
        return next_portfolio

    should_rebalance = get_should_rebalance(
        strategy_info["rebalancing"], date, portfolio["rebalanced_at"])

    rebalancing_list = create_rebalancing_list(
        portfolio, weights, prices) if should_rebalance else []

    transactions = create_transactions(
        rebalancing_list, date, portfolio["commission"])

    transactions_commissions = get_transactions_commissions(
        transactions)
    transactions_cash_flow = get_transactions_cash_flow(transactions)
    cash = portfolio["cash"] + transactions_cash_flow

    positions = update_positions(portfolio["positions"], transactions)
    positions = update_positions_values_and_weights(positions, prices)

    positions_market_value = get_positions_market_value(
        positions, portfolio["currency"], prices)

    new_portfolio = {
        "strategy_ticker": portfolio["strategy_ticker"],
        "currency": portfolio["currency"],
        "cash": cash,
        # TODO as external input, dependent on currency acutally!
        "commission": portfolio["commission"],
        "positions": positions,
        "transactions": transactions,
        "date": date,
        "positions_market_value": positions_market_value,
        "total_value": cash + positions_market_value,
        "commissions_paid": transactions_commissions,
        "total_commissions_paid": transactions_commissions + portfolio["commissions_paid"],
        "rebalanced_at": date if should_rebalance else portfolio["rebalanced_at"],
        "strategy_weights": weights
    }

    return new_portfolio
