import pandas as pd
import numpy as np

def GetTurtle(df, period):
    df = df.assign(Close_1_shift = df["Close"].shift(1))
    df = df.assign(TR = np.abs(df.High - df.Low))
    df = df.assign(TR = np.maximum(
        df["TR"],
        np.maximum(
            np.abs(df.Close_1_shift - df.High),
            np.abs(df.Close_1_shift - df.Low),
        ),
    ))
    # The N value from Turtle Algorithm
    n_array = np.array(df["TR"].values)
    n_array[period] = np.mean(df["TR"][:period])
    for i in range(period+1, df.shape[0]):
        n_array[i] = (float(period-1) * n_array[i - 1] + df["TR"][i]) / float(period)
    df = df.assign(N = n_array)

    # Compute upper and lower bounds based on Turtle Algorithm
    df = df.assign(lower_bound = df["Low"].shift(1).rolling(window=int(period/2)).min())

    price = df["Close"].iloc[-1]
    sl = np.ceil((price - 2.0 * df["N"].iloc[-1])*100)/100
    # sl = np.ceil(((((price - 2.0 * df["N"].iloc[i])+price)/2+price)/2+price)/2*100)/100

    if price < sl or price <  df["lower_bound"].iloc[-1]:
        return -1
    return 1

def GetTurtleOrigin(df, period):
    # # 5-days high
    # df = df. assign(hh = df.Close.shift(1).rolling(window=period).max())
    # # 5-days low
    df = df. assign(ll = df.Close.shift(1).rolling(window=period).min())
    # 5-days mean
    # df = df. assign(avg = df.Close.shift(1).rolling(window=period).mean())

    if df.iloc[-1].Close < df.iloc[-1].ll:
        return -1
    return 1



# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="365d")
# turtle = GetTurtle(df,4)
# print(turtle)