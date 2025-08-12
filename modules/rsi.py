import numpy as np

def Rsi(wilder_data):
    rsi = 0
    window_length = 14
    # Initialize containers for avg. gains and losses
    gains = []
    losses = []
    # Create a container for current lookback prices
    window = []
    # Keeps track of previous average values
    prev_avg_gain = None
    prev_avg_loss = None
    # Create a container for our final output (as a csv)
    output = [['date', 'close', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rsi']]

    for i, price in enumerate(wilder_data):
        # keep track of the price for the first period
        # but don't calculate a difference value.
        if i == 0:
            window.append(price)
            output.append([i+1, price, 0, 0, 0, 0, 0])
            continue
        # After the first period, calculate the difference
        # between price and previous price as a rounded value
        difference = round(wilder_data[i] - wilder_data[i - 1], 2)

        if difference > 0:
            gain = difference
            loss = 0
        # Record negative differences as losses
        elif difference < 0:
            gain = 0
            loss = abs(difference)
        # Record no movements as neutral
        else:
            gain = 0
            loss = 0
        # Save gains/losses
        gains.append(gain)
        losses.append(loss)
        # Continue to iterate until enough
        # gains/losses data is available to 
        # calculate the initial RS value
        if i < window_length:
            window.append(price)
            output.append([i+1, price, gain, loss, 0, 0, 0])
            continue

        if i == window_length:
            avg_gain = sum(gains) / len(gains)
            avg_loss = sum(losses) / len(losses)
        # Use WSM after initial window-length period
        else:
            avg_gain = (prev_avg_gain * (window_length - 1) + gain) / window_length
            avg_loss = (prev_avg_loss * (window_length - 1) + loss) / window_length
        # Keep in memory
        prev_avg_gain = avg_gain
        prev_avg_loss = avg_loss
        # Round for later comparison (optional)
        avg_gain = round(avg_gain, 2)
        avg_loss = round(avg_loss, 2)
        prev_avg_gain = round(prev_avg_gain, 2)
        prev_avg_loss = round(prev_avg_loss, 2)

        if avg_loss == 0: avg_loss = 1
        rs = round(avg_gain / avg_loss, 2)

        rsi = round(100 - (100 / (1 + rs)), 2)

        window.append(price)
        window.pop(0)
        gains.pop(0)
        losses.pop(0)
        # Save Data
        output.append([i+1, price, gain, loss, avg_gain, avg_loss, rsi])

    output.pop(0)
    output = np.array(output)
    rsi = output[:,6]
    return rsi

# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="max")
# closedf = df[['Close']]
# closeArr = closedf.Close.values.tolist()
# # print(closeArr)
# rsi = Rsi(closeArr)
# df = df.assign(Rsi=rsi)
# print(df.Rsi)

def RsiDf(df):
    column = df.columns[0]
    delta = df[column].diff(1)
    delta = delta.dropna()
    up = delta.copy()
    down = delta.copy()
    up[up<0] = 0
    down[down>0] = 0
    df = df.assign(up=up)
    df = df.assign(down=down)
    upArr = df.up.values.tolist()
    downArr = df.down.values.tolist()
    avgGain = df.up.mean()
    avgLoss = abs(df.down.mean())
    rs = avgGain / avgLoss
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return rsi

import numpy as np
# from numba import njit

def GetRsi(close_prices, window=14):
    delta = np.diff(close_prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    
    avg_gain = np.convolve(gain, np.ones((window,))/window, mode='valid')
    avg_loss = np.convolve(loss, np.ones((window,))/window, mode='valid')
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Pad the RSI array to match the length of the input
    rsi = np.concatenate([np.full(window-1, np.nan), rsi])
    return rsi

import pandas as pd
def get_rsi(npArr, period = 14):
    columns =  ['d']
    df = pd.DataFrame(npArr, columns = columns)
    c = df['d']
    diff = c.diff() #前日比
    up = diff.copy() #上昇
    down = diff.copy() #下落
    up = up.where(up > 0, np.nan) #上昇以外はnp.nan
    down = down.where(down < 0, np.nan) #下落以外はnp.nan
    #upma = up.rolling(window=period).mean() #平均
    #downma = down.abs().rolling(window=period).mean() #絶対値の平均
    upma = up.ewm(span=period,adjust=False).mean() #平均
    downma = down.abs().ewm(span=period,adjust=False).mean() #絶対値の平均
    rs = upma / downma
    rsi = 100 - (100 / (1.0 + rs))
    return rsi.values.tolist()