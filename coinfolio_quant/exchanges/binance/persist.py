from .binance import get_positions
from ...datalake.client_portfolios import persist_portfolio_snapshot


def persist_all_portfolio_snapshots(database, users_list):
    for user in users_list:
        user_id = user["id"]
        binance_account = user["binanceAccount"]

        if binance_account is not None:
            print("rebalancing binance portfolio for " + user["email"])
            api_key = binance_account["apiKey"]
            api_secret = binance_account["apiSecret"]
            account_name = binance_account["name"]

            positions = get_positions(
                api_key=api_key, api_secret=api_secret, account_name=account_name)

            persist_portfolio_snapshot(
                database=database, positions=positions, client_id=user_id)

            print("successfully rebalanced binance portfolio for " +
                  user["email"])
