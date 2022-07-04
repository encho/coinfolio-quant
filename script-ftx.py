import pandas as pd
import requests
import time
import urllib.parse
from typing import Optional, Dict, Any, List
from requests import Request, Session, Response, get
import hmac
import os
from prettyprinter import pprint


class FtxClient:
    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, api_key=None, api_secret=None, subaccount_name=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name

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

    def place_order(self, market: str, side: str, price: float, size: float, client_id: str,
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

    def get_markets(self) -> List[dict]:
        return self._get(f'markets')

    def get_open_orders(self, order_id: int, market: str = None) -> List[dict]:
        return self._get(f'orders', {'market': market, 'order_id': order_id})

    def get_wallet_balances(self) -> List[dict]:
        return self._get(f'wallet/balances')


markets = get('https://ftx.com/api/markets').json()
df = pd.DataFrame(markets['result'])
df.set_index('name', inplace=True)
df.T

print(df)


markets = get(
    'https://ftx.com/api/markets/AAPL/USD').json()

apple = pd.DataFrame(markets)
apple = apple.drop(['success'], axis=1)
apple

print(apple)
# markets = pd.DataFrame(requests.get(
#     'https://ftx.com/api/markets/BTC-0924').json())
# markets = markets.drop(['success'], axis=1)
# markets


FTX_API_KEY = os.environ["FTX_API_KEY"]
FTX_API_SECRET = os.environ["FTX_API_SECRET"]

print("~~~~~~~~~~~ ftx ~~~~~~~~~~")
print(FTX_API_KEY)
print(FTX_API_SECRET)

c = FtxClient(api_key=FTX_API_KEY, api_secret=FTX_API_SECRET)

balances = c.get_wallet_balances()

markets = c.get_markets()

pprint(balances)
pprint(markets)

markets_filtered = list(
    filter(lambda it: it["quoteCurrency"] == "USD" and it["baseCurrency"] == "BTC", markets))

pprint(markets_filtered)
