import os
from binance.spot import Spot

api_key = os.environ["API_KEY"]
api_secret = os.environ["API_SECRET"]

client = Spot(key=api_key, secret=api_secret)

# Get account information
# print(client.account())

# Post a new order
# params = {
#     'symbol': 'BTCUSDT',
#     'side': 'SELL',
#     'type': 'LIMIT',
#     'timeInForce': 'GTC',
#     'quantity': 0.002,
#     'price': 9500
# }

# response = client.new_order(**params)
# print(response)


def get_positions():
    info = client.account()
    balances = info["balances"]
    parsed_balances = map(lambda balance: {"asset": balance["asset"], "free": float(
        balance["free"]), "locked": float(balance["locked"])}, balances)
    positive_balances = list(filter(
        lambda balance: balance["free"] > 0 or balance["locked"] > 0, parsed_balances))

    assets = list(map(lambda b: b["asset"], positive_balances))

    account_coin = "USDT"

    symbols_for_pricing = [asset + account_coin for asset in assets]
    symbol_prices = client.ticker_price(symbols=symbols_for_pricing)
    parsed_symbol_prices = list(
        map(lambda it: {"symbol": it["symbol"], "price": float(it["price"])}, symbol_prices))

    positions = [
        {"symbol": price["symbol"],
            "asset": balance["asset"],
            "value": (balance["free"] + balance["locked"]) * price["price"],
            "price": float(price["price"])
         } for (balance, price) in zip(positive_balances, parsed_symbol_prices)]

    positions = [
        {
            # "symbol": price["symbol"],
            "ticker": balance["asset"],
            "quantity": (balance["free"] + balance["locked"]),
            # QUICK-FIX better name xxxValue: [20.44, "USDT"]
            "usdValue": (balance["free"] + balance["locked"]) * price["price"],
            "price": float(price["price"])
        } for (balance, price) in zip(positive_balances, parsed_symbol_prices)]

    total_value = 0
    for position in positions:
        total_value += position["usdValue"]

    for position in positions:
        position["weight"] = position["usdValue"] / total_value

    return positions


positions = get_positions()
print("*******")
print("Positions")
print("*******")
print(positions)
