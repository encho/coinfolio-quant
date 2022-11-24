from binance.spot import Spot
import datetime
# import numpy as np
from coinfolio_quant.portfolio.rebalancing import create_target_positions, get_total_positions_value, create_liquidations, create_rebalancing_buys
from coinfolio_quant.quant_utils import asset_allocation_utils
# import math
from decimal import Decimal, ROUND_DOWN
from prettyprinter import pprint


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


# import time
# import urllib.parse
# from typing import Optional, Dict, Any, List
# from requests import Request, Session, Response, get
# import hmac
# from prettyprinter import pprint
# from ...quant_utils import asset_allocation_utils

# from coinfolio_quant.portfolio.rebalancing import create_target_positions, get_total_positions_value, create_liquidations, create_rebalancing_buys
# a mapping which defines which assets on FTX should be taken as a proxy instrument
# for any given key (e.g. "XAU" in our system would be implemented with "PAXG" on FTX exchange)
FTX_ASSET_PROXIES = {"XAU": "PAXG"}


def get_positionsOLD(api_key, api_secret, account_name):
    client = Spot(key=api_key, secret=api_secret)

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


def get_positions(api_key, api_secret, account_name):
    client = Spot(key=api_key, secret=api_secret)
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


def rebalance_portfolio(api_key, api_secret, account_name, target_weights):
    client = Spot(key=api_key, secret=api_secret)

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

    print("^^^^^^^")

    # 0. replace tickers with the proxy-tickers for FTX
    target_weights = asset_allocation_utils.insert_assets_proxies(
        target_weights, FTX_ASSET_PROXIES)

    print("----------------------")
    print("target_weights")
    print("----------------------")
    print(target_weights)

    # 1. get current positions and total portfolio value
    positions = get_positions(
        api_key=api_key, api_secret=api_secret, account_name=account_name)
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
    liquidated_positions = get_positions(
        api_key=api_key, api_secret=api_secret, account_name=account_name)

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
    target_positions_post_liquidations = create_target_positions(
        target_weights, liquidated_total_portfolio_value, market_data_list_post_liquidations, quote_currency="USDT")
    print("----------------------")
    print("target_positions_post_liquidations")
    print("----------------------")
    print(target_positions_post_liquidations)

    # 10. get rebalancing buys
    rebalancing_buys = create_rebalancing_buys(
        target_positions_post_liquidations, liquidated_positions,
        market_data_list_post_liquidations, quote_currency="USDT")
    print("----------------------")
    print("rebalancing_buys NEW")
    print("----------------------")
    print(rebalancing_buys)

    # 11. execute rebalancing buys
    def execute_rebalancing_buys(the_rebalancing_buys, account_currency="USDT"):
        for rebalancing_buy in the_rebalancing_buys:
            ticker = rebalancing_buy["ticker"]
            market = ticker + account_currency
            buy_quantity = rebalancing_buy["ideal_buy_quantity"]

            market_info = find_unique(
                lambda it: it["baseCurrency"] == ticker and it["quoteCurrency"] == account_currency, market_data_list_post_liquidations)

            lotted_buy_quantity = float(Decimal(buy_quantity).quantize(
                Decimal(market_info["stepSize"]), rounding=ROUND_DOWN))

            lotted_buy_quantity_string = str(lotted_buy_quantity)
            has_exp = "e" in lotted_buy_quantity_string

            if has_exp:
                step_size = market_info["stepSize"]
                number_of_digits = len(step_size.split(".")[1])
                fmt_string = '{:.' + str(number_of_digits) + 'f}'
                clean_lotted_buy_quantity_string = fmt_string.format(
                    lotted_buy_quantity)
            else:
                clean_lotted_buy_quantity_string = str(
                    lotted_buy_quantity_string)

            try:
                if buy_quantity > 0:
                    place_order(market=market, side="BUY",
                                price=None,
                                size=clean_lotted_buy_quantity_string,
                                type="MARKET", client_id="N/A")

            except Exception as e:
                # TODO log this and eventually have a look in the ui as well
                print(f'Error making buy order request: {e}')

    execute_rebalancing_buys(rebalancing_buys)

# def get_orders(api_key, api_secret, account_name):
#     c = FtxClient(api_key=api_key, api_secret=api_secret,
#                   account_name=account_name)
#     return c.get_orders()


def get_orders_history(api_key, api_secret, account_name):
    client = Spot(key=api_key, secret=api_secret)

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
            # "future": np.nil,
            "future": "N/A",
            "id": order["orderId"],
            "clientId": order["clientOrderId"],
            "timestamp": int(order["time"])
        }

    symbols = [
        "ETHBTC",
        "BTCUSDT",
        "ETHUSDT",
        "PAXGUSDT",
    ]

    orders = []
    for symbol in symbols:
        new_orders = client.get_orders(symbol)
        new_parsed_orders = list(
            map(lambda order: parse_order(order), new_orders))
        orders.extend(new_parsed_orders)

    orders.sort(key=lambda order: order["timestamp"])

    return orders

# def get_account(api_key, api_secret, account_name):
#     c = FtxClient(api_key=api_key, api_secret=api_secret,
#                   account_name=account_name)
#     return c.get_account()
