
def insert_assets_proxies(target_weights, proxies_dict):
    target_weights_substituted = []
    for target_weight_dict in target_weights:
        ticker = target_weight_dict["ticker"]
        weight = target_weight_dict["weight"]
        new_ticker = proxies_dict.get(ticker, ticker)
        edited_target_weight_dict = {"ticker": new_ticker, "weight": weight}
        target_weights_substituted.append(edited_target_weight_dict)
    return target_weights_substituted


test_asset_proxies = {"XAU": "PAXG"}

test_target_weights = [
    {"ticker": "BTC", "weight": 0.60},
    {"ticker": "XAU", "weight": 0.40},
]

test_proxy_target_weights = [
    {"ticker": "BTC", "weight": 0.60},
    {"ticker": "PAXG", "weight": 0.40},
]

assert insert_assets_proxies(
    test_target_weights, test_asset_proxies) == test_proxy_target_weights
