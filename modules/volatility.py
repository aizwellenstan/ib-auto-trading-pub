import pandas as pd

def GetVolatility(symbol_a,symbol_b):
    column = symbol_a.columns[0]
    volatility_ratio = (
        symbol_a[column].pct_change().dropna().std() / 
        symbol_b[column].pct_change().dropna().std()
    )

    return volatility_ratio

def GetOverBoughtSold(symbol_a,symbol_b):
    column = symbol_a.columns[0]
    beta = symbol_a[column].mean() / symbol_b[column].mean()
    last_price_a = symbol_a[column].dropna().values[-1]
    last_price_b = symbol_b[column].dropna().values[-1]

    expected_last_price_a = last_price_b * beta

    overBoughtSold = last_price_a / expected_last_price_a

    return overBoughtSold

# def calculate_signals():

#     is_up_trend, is_down_trend = self.volatility_ratio > 1, self.volatility_ratio < 1
#     is_overbought, is_oversold = self.is_overbought_or_oversold()

#     # Our final trade signals
#     self.is_buy_signal = is_up_trend and is_oversold
#     self.is_sell_signal = is_down_trend and is_overbought

# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="365d")
# df = df[['Close']]

# stockInfo = yf.Ticker("^N225")
# spyDf = stockInfo.history(period="365d")
# print(spyDf)
# spyDf = spyDf[['Close']]

# volatility = GetVolatility(df,spyDf)
# volatility = GetOverBoughtSold(df,spyDf)
# print(volatility)