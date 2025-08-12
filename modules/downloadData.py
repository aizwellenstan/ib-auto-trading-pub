from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
from aiztradingview import GetProfitJP
from datetime import date, datetime
import pandas as pd

#東証コードのリストを取得
# codes = GetProfitJP()

# for code in codes:
#     print(code)
#     my_share = share.Share(code + ".T")
#     symbol_data = None

#     try:
#         # symbol_data = my_share.get_historical(share.PERIOD_TYPE_DAY,
#         #                                     100,
#         #                                     share.FREQUENCY_TYPE_HOUR,
#         #                                     1)
#         symbol_data = my_share.get_historical(share.PERIOD_TYPE_DAY,
#                                             36500,
#                                             share.FREQUENCY_TYPE_DAY,
#                                             1)
#     except YahooFinanceError as e:
#         print(e.message)

#     print(symbol_data)
    
#     #csv形式で保存
#     if (symbol_data == None):
#         continue

#     df = pd.DataFrame({'datetime': [datetime.fromtimestamp(d / 1000) for d in symbol_data['timestamp']],\
#         'Open' : symbol_data['open'], 'High' : symbol_data['high'],\
#         'Close' : symbol_data['close'], 'Volume' : symbol_data['volume']})
    
#     print(df)

# import yfinance as yf
# stockInfo = yf.Ticker("3359.T")
# hist = stockInfo.history(period="36500d")
# hist = hist.dropna()
# print(hist)

my_share = share.Share("QQQ")
symbol_data = None

try:
    # symbol_data = my_share.get_historical(share.PERIOD_TYPE_DAY,
    #                                     100,
    #                                     share.FREQUENCY_TYPE_HOUR,
    #                                     1)
    symbol_data = my_share.get_historical(share.PERIOD_TYPE_DAY,
                                        36500,
                                        share.FREQUENCY_TYPE_MINUTE,
                                        1)
except YahooFinanceError as e:
    print(e.message)

print(symbol_data)

#csv形式で保存
if (symbol_data == None): print("None")

df = pd.DataFrame({'datetime': [datetime.fromtimestamp(d / 1000) for d in symbol_data['timestamp']],\
    'Open' : symbol_data['open'], 'High' : symbol_data['high'],\
    'Close' : symbol_data['close'], 'Volume' : symbol_data['volume']})

print(df)