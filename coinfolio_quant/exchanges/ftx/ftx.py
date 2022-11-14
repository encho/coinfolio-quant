import time
import urllib.parse
from typing import Optional, Dict, Any, List
from requests import Request, Session, Response, get
import hmac
from prettyprinter import pprint
from ...quant_utils import asset_allocation_utils

from coinfolio_quant.portfolio.rebalancing import create_target_positions, get_total_positions_value, create_liquidations, create_rebalancing_buys


# a mapping which defines which assets on FTX should be taken as a proxy instrument
# for any given key (e.g. "XAU" in our system would be implemented with "PAXG" on FTX exchange)
FTX_ASSET_PROXIES = {"XAU": "PAXG"}


class FtxClient:
    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, api_key=None, api_secret=None, account_name=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret

        self._subaccount_name = account_name
        if account_name == "Main Account":
            # self._subaccount_name = "Coinfolio"
            self._subaccount_name = None

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode(
        )
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(),
                             signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)

        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(
                self._subaccount_name)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']

    def place_order(self, market: str, side: str, price: float, size: float, client_id: str = None,
                    type: str = 'limit', reduce_only: bool = False, ioc: bool = False, post_only: bool = False,
                    ) -> dict:
        return self._post('orders', {'market': market,
                                     'side': side,
                                     'price': price,
                                     'size': size,
                                     'type': type,
                                     'reduceOnly': reduce_only,
                                     'ioc': ioc,
                                     'postOnly': post_only,
                                     'clientId': client_id,
                                     })

    def get_open_orders(self, order_id: int, market: str = None) -> List[dict]:
        return self._get(f'orders', {'market': market, 'order_id': order_id})

    def execute_liquidation(self, ticker: str, size: float, into: str = 'USD', client_id: str = None):
        # e.g. BTC/USD
        market = ticker + "/" + into
        try:
            self.place_order(market=market, side="sell", price=None,
                             size=size, client_id=client_id, type="market")
        except Exception as e:
            # TODO log this and eventually have a look in the ui as well
            print(f'Error making liquidation order request: {e}')

    def get_markets(self) -> List[dict]:
        return self._get(f'markets')

    def get_account(self) -> List[dict]:
        return self._get(f'account')

    def get_positions(self) -> List[dict]:
        wallet_balances = self._get(f'wallet/balances')

        total_usd_value = 0
        for wallet in wallet_balances:
            total_usd_value = total_usd_value + wallet["usdValue"]

        positions = [{"ticker": item["coin"], "quantity": item["total"],
                      "usdValue": item["usdValue"], "weight": item["usdValue"] / total_usd_value} for item in wallet_balances if item["total"] > 0]

        return positions

    def get_orders(self) -> List[dict]:
        orders = self._get(f'orders')
        return orders

    def get_orders_history(self) -> List[dict]:
        orders_history = self._get(f'orders/history')
        return orders_history

    def execute_liquidations(self, liquidations):
        for liquidation in liquidations:
            self.execute_liquidation(ticker=liquidation["ticker"],
                                     size=liquidation["liquidation_quantity"],
                                     into="USD"
                                     )

    def execute_rebalancing_buys(self, rebalancing_buys):
        for rebalancing_buy in rebalancing_buys:
            ticker = rebalancing_buy["ticker"]
            market = ticker + "/USD"
            buy_quantity = rebalancing_buy["buy_quantity"]

            if buy_quantity > 0:
                self.place_order(market=market, side="buy",
                                 price=None, size=buy_quantity, type="market")

    def trigger_rebalance(self, target_weights):

        # 0. replace tickers with the proxy-tickers for FTX
        target_weights = asset_allocation_utils.insert_assets_proxies(
            target_weights, FTX_ASSET_PROXIES)

        # 1. get current positions and total portfolio value
        positions = self.get_positions()
        total_portfolio_value = get_total_positions_value(positions)

        # 2. get current market data list
        market_data_list = self.get_markets()

        # 3. create ideal market positions (respecting lot sizes)
        target_positions = create_target_positions(
            target_weights, total_portfolio_value, market_data_list)

        # 4. determine liquidations into USD
        liquidations = create_liquidations(positions, target_positions)

        # 5. exectue liquidations into USD
        self.execute_liquidations(liquidations)

        # 6. get liquidated positions
        liquidated_positions = self.get_positions()

        # 7. determine new portfolio value
        liquidated_total_portfolio_value = get_total_positions_value(
            liquidated_positions)

        # 8. get updated market data list
        market_data_list_post_liquidations = self.get_markets()

        # 9. determine new target_positions
        target_positions_post_liquidations = create_target_positions(
            target_weights, liquidated_total_portfolio_value, market_data_list_post_liquidations)

        # 10. get rebalancing buys
        rebalancing_buys = create_rebalancing_buys(
            target_positions_post_liquidations, liquidated_positions, market_data_list_post_liquidations)

        # 11. execute rebalancing buys
        self.execute_rebalancing_buys(rebalancing_buys)


# TODO deprecate, use directly in app.py
def get_positions(api_key, api_secret, account_name):
    c = FtxClient(api_key=api_key, api_secret=api_secret,
                  account_name=account_name)
    return c.get_positions()


# TODO deprecate, use directly in app.py
def rebalance_portfolio(api_key, api_secret, account_name, target_weights):
    c = FtxClient(api_key=api_key, api_secret=api_secret,
                  account_name=account_name)
    return c.trigger_rebalance(target_weights)


# TODO deprecate, use directly in app.py
def get_orders(api_key, api_secret, account_name):
    c = FtxClient(api_key=api_key, api_secret=api_secret,
                  account_name=account_name)
    return c.get_orders()


# TODO deprecate, use directly in app.py
def get_orders_history(api_key, api_secret, account_name):
    c = FtxClient(api_key=api_key, api_secret=api_secret,
                  account_name=account_name)
    return c.get_orders_history()


# TODO deprecate, use directly in app.py
def get_account(api_key, api_secret, account_name):
    c = FtxClient(api_key=api_key, api_secret=api_secret,
                  account_name=account_name)
    return c.get_account()
