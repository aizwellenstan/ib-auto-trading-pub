import alpaca_trade_api as tradeapi

def GetShortable():
    api = tradeapi.REST(,
                        secret_key="",
                        base_url='https://paper-api.alpaca.markets')
    shortable_list = [l for l in api.list_assets() if l.shortable]

    shortableSymList = []
    for sym in shortable_list:
        shortableSymList.append(sym.symbol)
        
    return shortableSymList