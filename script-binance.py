import os
import datetime
from binance.spot import Spot
from coinfolio_quant.portfolio.rebalancing import create_target_positions, get_total_positions_value, create_liquidations, create_rebalancing_buys
from coinfolio_quant.quant_utils import asset_allocation_utils
from prettyprinter import pprint
import math
from decimal import Decimal, ROUND_DOWN

api_key = os.environ["API_KEY"]
api_secret = os.environ["API_SECRET"]


# a mapping which defines which assets on Binance should be taken as a proxy instrument
# for any given key (e.g. "XAU" in our system would be implemented with "PAXG" on Binance exchange)
BINANCE_ASSET_PROXIES = {"XAU": "PAXG"}

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


def find_unique(predicate, data):
    filtered_items = list(filter(predicate, data))

    if len(filtered_items) != 1:
        raise Exception(
            "Could not find exactly one match for the predicate.")

    return filtered_items[0]


def find_unique_or_default(predicate, data, default_value):
    filtered_items = list(filter(predicate, data))

    if len(filtered_items) != 1:
        return default_value

    return filtered_items[0]


def removeTrailingZerosInString(s):
    while s[-1] == "0":
        s = s[:-1]
    return s


def get_markets(symbols):
    symbols_prices = client.ticker_price(symbols=symbols)
    exchange_info = client.exchange_info(symbols=symbols)

    market_data_list = []
    for symbol in symbols:
        price_item = find_unique(
            lambda it: it["symbol"] == symbol, symbols_prices)
        info_item = find_unique(
            lambda it: it["symbol"] == symbol, exchange_info["symbols"])
        lot_size_spec = find_unique(
            lambda it: it["filterType"] == "LOT_SIZE", info_item["filters"])

        market_data_item = {
            "baseCurrency": info_item["baseAsset"],
            "quoteCurrency": info_item["quoteAsset"],
            "price": float(price_item["price"]),
            "minProvideSize": float(lot_size_spec["stepSize"]),
            "stepSize": removeTrailingZerosInString(lot_size_spec["stepSize"])
        }
        market_data_list.append(market_data_item)

    market_data_list.append(
        {"baseCurrency": "USDT", "quoteCurrency": "USDT", "minProvideSize": 0.00001, "stepSize": "0.00001", "price": 1})
    return market_data_list


def get_positions():
    info = client.account()
    balances = info["balances"]
    parsed_balances = map(lambda balance: {"asset": balance["asset"], "free": float(
        balance["free"]), "locked": float(balance["locked"])}, balances)
    positive_balances = list(filter(
        lambda balance: balance["free"] > 0 or balance["locked"] > 0, parsed_balances))

    assets = list(map(lambda b: b["asset"], positive_balances))

    account_coin = "USDT"

    # remove account coin from assets
    assets.remove(account_coin)

    symbols_for_pricing = [asset + account_coin for asset in assets]
    symbol_prices = client.ticker_price(symbols=symbols_for_pricing)
    parsed_symbol_prices = list(
        map(lambda it: {"symbol": it["symbol"], "price": float(it["price"])}, symbol_prices))

    positions = []
    for positive_balance in positive_balances:
        asset = positive_balance["asset"]
        symbol = asset + account_coin
        amount = positive_balance["free"] + positive_balance["locked"]
        price_item = find_unique_or_default(
            lambda it: it["symbol"] == symbol, parsed_symbol_prices, None)
        price = 1 if price_item is None else price_item["price"]
        value = amount * price
        positions.append({
            "symbol": symbol,
            "ticker": asset,
            # QUICK-FIX better name xxxValue: [20.44, "USDT"]
            "usdValue": value,
            "price": price,
            "quantity": amount
        })

    total_value = 0
    for position in positions:
        total_value += position["usdValue"]

    for position in positions:
        position["weight"] = position["usdValue"] / total_value

    return positions


def get_order_history():
    def parse_order(order):
        created_at = datetime.datetime.utcfromtimestamp(order["time"] / 1e3)
        return {
            "price": float(order["price"]),
            "avgFillPrice": float(order["price"]),
            "side": order["side"],
            "size": float(order["origQty"]),
            "remainingSize": float(order["origQty"]) - float(order["executedQty"]),
            "type": order["type"],
            "status": order["status"],
            "market": order["symbol"],
            "createdAt": created_at.isoformat(),
            "filledSize": float(order["executedQty"]),
            "future": False,
            "id": order["orderId"],
            "clientId": order["clientOrderId"],
        }

    # TODO parse order into this format
    #   //   avgFillPrice: numOrNull(order.avgFillPrice),
    #   //   createdAt: str(order.createdAt),
    #   //   filledSize: num(order.filledSize),
    #   //   future: strOrNull(order.future),
    #   //   id: num(order.id),
    #   //   market: str(order.market),
    #   //   price: numOrNull(order.price),
    #   //   remainingSize: num(order.remainingSize),
    #   //   side: orderSide(order.side),
    #   //   size: num(order.size),
    #   //   status: orderStatus(order.status),
    #   //   type: orderType(order.type),
    #   //   clientId: maybeStr(order.clientId),
    orders = client.get_orders("ETHBTC")
    print("..........")
    print(orders)
    print("..........")

    parsed_orders = list(map(lambda order: parse_order(order), orders))

    return parsed_orders


# positions = get_positions()
# print("*******")
# print("Positions")
# print("*******")
# print(positions)

# order_history = get_order_history()
# print("*******")
# print("Order History")
# print("*******")
# print(order_history)


def rebalance_portfolio(api_key, api_secret, account_name, target_weights):
    print("^^^^^^^")
    # print(api_key)
    # print(api_secret)
    # print(account_name)
    # print(target_weights)

    # 0. replace tickers with the proxy-tickers for Binance
    target_weights = asset_allocation_utils.insert_assets_proxies(
        target_weights, BINANCE_ASSET_PROXIES)

    print("----------------------")
    print("target_weights")
    print("----------------------")
    print(target_weights)

    # 1. get current positions and total portfolio value
    positions = get_positions()
    total_portfolio_value = get_total_positions_value(positions)

    print("----------------------")
    print("positions")
    print("----------------------")
    print(positions)

    print("----------------------")
    print("total_portfolio_value")
    print("----------------------")
    print(total_portfolio_value)

    # 2. get current market data list
    base_quote_pairs = [["ETH", "USDT"], ["BTC", "USDT"], ["PAXG", "USDT"]]
    symbols_for_pricing = [
        base + quote for [base, quote] in base_quote_pairs]

    market_data_list = get_markets(symbols_for_pricing)
    print("----------------------")
    print("market_data_list")
    print("----------------------")
    print(market_data_list)

    # 3. create ideal market positions (respecting lot sizes)
    # target_positions = create_target_positions(
    #     target_weights, total_portfolio_value, market_data_list, quote_currency="BTC")
    target_positions = create_target_positions(
        target_weights, total_portfolio_value, market_data_list, quote_currency="USDT")
    print("----------------------")
    print("target_positions")
    print("----------------------")
    print(target_positions)

    # 4. determine liquidations into USD
    liquidations = create_liquidations(
        positions, target_positions, account_currency="USDT")
    print("----------------------")
    print("liquidations")
    print("----------------------")
    print(liquidations)

    # 5. exectue liquidations into USD
    def place_order(market, side, price, size, client_id, type):
        client.new_order(market, side, type, quantity=size)

    def execute_liquidation(ticker, size, into):
        # e.g. BTCUSDT
        symbol = ticker + into
        # symbol = into + ticker
        try:
            if size > 0:
                place_order(market=symbol, side="SELL", price=None,
                            size=size, client_id="N/A", type="MARKET")
        except Exception as e:
            # TODO log this and eventually have a look in the ui as well
            print(f'Error making liquidation order request: {e}')

    # def execute_liquidations(the_liquidations):
    #     for liquidation in the_liquidations:
    #         execute_liquidation(ticker=liquidation["ticker"],
    #                             size=liquidation["liquidation_quantity"],
    #                             into="BTC"
    #                             )
    def execute_liquidations(the_liquidations, the_market_data_list):
        quote_currency = "USDT"
        for liquidation in the_liquidations:
            asset = liquidation["ticker"]
            market_info = find_unique(
                lambda it: it["baseCurrency"] == asset and it["quoteCurrency"] == quote_currency, market_data_list)
            # lotted_liquidation_size = math.floor(
            #     liquidation["liquidation_quantity"] / market_info["minProvideSize"]) * market_info["minProvideSize"]

            # lotted_liquidation_size = float(Decimal(liquidation["liquidation_quantity"]).quantize(Decimal('0.00001'), rounding=ROUND_DOWN))
            lotted_liquidation_size = float(Decimal(liquidation["liquidation_quantity"]).quantize(
                Decimal(market_info["stepSize"]), rounding=ROUND_DOWN))

            print("lotted liquidation size: " + asset)
            print(lotted_liquidation_size)
            execute_liquidation(ticker=liquidation["ticker"],
                                size=lotted_liquidation_size,
                                into=quote_currency
                                )
    execute_liquidations(liquidations, market_data_list)

    # 6. get liquidated positions
    liquidated_positions = get_positions()

    print("----------------------")
    print("liquidated_positions")
    print("----------------------")
    print(liquidated_positions)

    # 7. determine new portfolio value
    liquidated_total_portfolio_value = get_total_positions_value(
        liquidated_positions)

    print("----------------------")
    print("liquidated_total_portfolio_value")
    print("----------------------")
    print(liquidated_total_portfolio_value)

    # 8. get updated market data list
    market_data_list_post_liquidations = get_markets(symbols_for_pricing)
    print("----------------------")
    print("market_data_list_post_liquidations")
    print("----------------------")
    print(market_data_list_post_liquidations)

    # 9. determine new target_positions
    # target_positions_post_liquidations = create_target_positions(
    #     target_weights, liquidated_total_portfolio_value, market_data_list_post_liquidations, quote_currency="BTC")
    target_positions_post_liquidations = create_target_positions(
        target_weights, liquidated_total_portfolio_value, market_data_list_post_liquidations, quote_currency="USDT")
    print("----------------------")
    print("target_positions_post_liquidations")
    print("----------------------")
    print(target_positions_post_liquidations)

    # 10. get rebalancing buys
    # rebalancing_buys = create_rebalancing_buys(
    #     target_positions_post_liquidations, liquidated_positions,
    #     market_data_list_post_liquidations, quote_currency="BTC")
    rebalancing_buys = create_rebalancing_buys(
        target_positions_post_liquidations, liquidated_positions,
        market_data_list_post_liquidations, quote_currency="USDT")
    print("----------------------")
    print("rebalancing_buys")
    print("----------------------")
    print(rebalancing_buys)

    # 11. execute rebalancing buys

    def execute_rebalancing_buys(the_rebalancing_buys, account_currency="USDT"):
        for rebalancing_buy in the_rebalancing_buys:
            ticker = rebalancing_buy["ticker"]
            market = ticker + account_currency
            buy_quantity = rebalancing_buy["buy_quantity"]

            if buy_quantity > 0:
                place_order(market=market, side="BUY",
                            price=None,
                            size=buy_quantity, type="MARKET", client_id="N/A")

                # place_order(market=symbol, side="SELL", price=None,
                #             size=size, client_id="N/A", type="MARKET")

    execute_rebalancing_buys(rebalancing_buys)


target_weights = [{'ticker': 'XAU', 'weight': 0.10}, {
    'ticker': 'BTC', 'weight': 0.70}]

rebalance_portfolio(api_key, api_secret, "test", target_weights)
