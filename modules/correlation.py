# import numpy as np
# import warnings
# from pandas_datareader import data as pdr
# import yfinance as yf
# import datetime as dt
# from yahoo_fin import stock_info as si
# import pandas as pd
# # pd.set_option('display.max_rows', None)
# warnings.filterwarnings("ignore")
# # yf.pdr_override()

# def GetCorrelation():
#     num_of_years = 1
#     start = dt.date.today() - dt.timedelta(days = int(365.25*num_of_years))
#     end = dt.date.today()

#     tickers = si.tickers_dow()

#     dataset = pdr.get_data_yahoo(tickers, start, end)['Adj Close']
#     stocks_returns = np.log(dataset/dataset.shift(1))
#     return get_top_abs_correlations(stocks_returns)

# def get_redundant_pairs(df):
#     pairs_to_drop = set()
#     cols = df.columns
#     for i in range(0, df.shape[1]):
#         for j in range(0, i+1):
#             pairs_to_drop.add((cols[i], cols[j]))
#     return pairs_to_drop

# def get_top_abs_correlations(df):
#     au_corr = df.corr().abs().unstack()
#     # labels_to_drop = get_redundant_pairs(df)
#     # au_corr = au_corr.drop(labels=labels_to_drop).sort_values(ascending=False)
#     return au_corr

# print(GetCorrelation())

import pandas as pd
data = pd.read_excel('https://global.oup.com/us/companion.websites/fdscontent/uscompanion/us/static/companion.websites/9780199734177/Example_1_rawdata.xls')
df = pd.DataFrame(data)
df.corr()