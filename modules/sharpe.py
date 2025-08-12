import numpy as np
import pandas as pd
from modules.data import GetDf

def get_return(nav_list):
    rtn_list = [0]
    for idx in range(1,len(nav_list)):
        rtn = (nav_list[idx]-nav_list[idx-1])/nav_list[idx-1]
        rtn_list.append(rtn)
    return rtn_list

def get_sharpe_ratio(nav_list,riskfree=0.0498):
    daily_return_list = get_return(nav_list)
    m = np.mean(daily_return_list)- riskfree/252
    s = np.std(daily_return_list)
    sharp_ratio = m/s*np.sqrt(252)
    return sharp_ratio

def get_annualized_return(nav_list):
    day_number = len(nav_list)
    final_rtn = nav_list[-1]
    n_year = day_number/float(252)
    if final_rtn > 0:
        a_rtn = final_rtn**(1/n_year)-1
    else:
        a_rtn = -1*((-1*final_rtn)**(1/n_year)-1)
    return a_rtn

def get_runup_list(nav_list):
    runup_list = []
    runup = 0
    for nav in nav_list:
        if nav > runup:
            runup = nav
        runup_list.append(runup)
    return runup_list

def get_drawdown_list(nav_list):
    runup_list = get_runup_list(nav_list)
    drawdown_list = []
    for idx in range(0, len(runup_list)):
        dd = (runup_list[idx]-nav_list[idx])/runup_list[idx]
        drawdown_list.append(dd)
    return drawdown_list

def get_mdd(nav_list):
    dd_list = get_drawdown_list(nav_list)
    return max(dd_list)

def get_carma_ratio(nav_list):
    return get_annualized_return(nav_list)/get_mdd(nav_list)

def Sharpe(adj, period = 120):
    adj = adj.astype(float)
    # Calculate returns
    returns = np.diff(adj) / adj[:-1]

    # Calculate rolling standard deviation
    rolling_std_dev = np.std(np.lib.stride_tricks.sliding_window_view(returns, window_shape=(period,)), axis=1)

    # Adjust the length of returns
    returns = returns[period-1:]

    # Calculate the expression
    result = (returns / rolling_std_dev)

    length = len(adj)
    length2 = len(result)
    diff = length - length2
    result = np.pad(result, (diff, 0), 'constant', constant_values=(0,))
    return result

def GetSharpe(df):
    mean = df.pct_change().rolling(252).mean()
    std = df.pct_change().rolling(252).std()
    sharpe = mean / std
    sharpe = float(sharpe.values[-1])

    return sharpe

def GetStd(df):
    std = df.pct_change().rolling(252).std()
    stdArr = std.values.tolist()
    std = stdArr[-1][0]

    return std

import numpy as np

def sharpe_ratio(return_series, N, rf):
    mean = return_series.mean() * N -rf
    sigma = return_series.std() * np.sqrt(N)
    return mean / sigma

def profolio(df):
    df = df.pct_change().dropna()
    df['Port'] = df.mean(axis=1)
    (df+1).cumprod()[-1:]
    return df

def GetSharpeRatio(df):
    df = df[['Close']]
    df = profolio(df)
    N = len(df) #255 trading days in a year
    rf = 0.01 #1% risk free rate
    sharpes = df.apply(sharpe_ratio, args=(N,rf,),axis=0)
    sharpe = sharpes.values[-1]

    return sharpe

def sortino_ratio(series, N, rf=0.04):
    mean = series.mean() * N -rf
    std_neg = series[series<0].std()*np.sqrt(N)
    return mean/std_neg

def GetSortinoNew(df):
    df = profolio(df)
    N = len(df) #255 trading days in a year
    rf = 0.01 #1% risk free rate
    sortinos = df.apply(sortino_ratio, args=(N,rf,), axis=0)
    sortino = sortinos.values[-1]

    return sortino

def GetSortino(df):
    df = profolio(df)
    N = 252 #255 trading days in a year
    rf = 0.01 #1% risk free rate
    sortinos = df.apply(sortino_ratio, args=(N,rf,), axis=0)
    sortino = sortinos.values[-1]

    return sortino

def SortinoRatio(close_prices, risk_free_rate=0.04737):
    returns = np.diff(close_prices) / close_prices[:-1]  # Calculate daily returns
    downside_returns = returns[returns < 0]  # Select only downside returns
    
    expected_return = np.mean(returns)  # Mean of all returns
    downside_deviation = np.std(downside_returns)  # Standard deviation of downside returns
    
    if downside_deviation != 0:
        sortino_ratio = (expected_return - risk_free_rate) / downside_deviation
    else:
        sortino_ratio = np.nan  # Handle the case where downside deviation is zero
    
    return sortino_ratio
    
def max_drawdown(return_series):
    comp_ret = (return_series+1).cumprod()
    peak = comp_ret.expanding(min_periods=1).max()
    dd = (comp_ret/peak)-1
    
    return dd.min()

def GetMaxDD(df):
    df = profolio(df)
    max_drawdowns = df.apply(max_drawdown,axis=0)
    maxDD = max_drawdowns.values[-1]

    return maxDD

def GetMDD(df):
    df = profolio(df)
    npArr = df.to_numpy()
    xs = npArr.cumsum()
    i = np.argmax(np.maximum.accumulate(xs) - xs)
    return i

def GteMDDR(a):
    a1 = a.cumsum()
    a2 = np.maximum.accumulate(a1)
    a3 = a2 - a1
    i = np.argmax(a3)
    r = (a2[i] - a1[i]) / a2[i]
    return r

def GetCalmar(df):
    df = profolio(df)
    max_drawdowns = df.apply(max_drawdown,axis=0)
    calmars = df.mean()*255/abs(max_drawdowns)
    calmar = calmars.values[-1]

    return calmar

def GetSterling(df):
    df = profolio(df)
    max_drawdowns = df.apply(max_drawdown,axis=0)
    calmars = df.mean()*255/(abs(max_drawdowns)-0.1)
    calmar = calmars.values[-1]

    return calmar

def GetSharpeRatioData(symbol):
    df = GetDf(symbol, 'USD', True)
    if len(df) < 1: return -1
    sharpe = GetSharpeRatio(df)
    return sharpe

# df = stocks.pct_change().dropna()
# df['Port'] = df.mean(axis=1) # 20% apple, ... , 20% facebook
# (df+1).cumprod().plot()

# (df+1).cumprod()[-1:]


# max_drawdowns = df.apply(max_drawdown,axis=0)

# calmars = df.mean()*255/abs(max_drawdowns)

# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="365d")
# df = df[['Close']]

# sharpe = GetSharpeRatio(df)
# print(sharpe)

# sortino = GetSortino(df)
# print(sortino)

# maxDD = GetMaxDD(df)
# print(maxDD)

# mdd = GetMDD(df)
# print(mdd)

# calmar = GetCalmar(df)
# print(calmar)

# sterling = GetSterling(df)
# print(sterling)

# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="365d")
# closedf = df[['Close']]
# maxDD = GetMaxDD(closedf)
# print(maxDD)
# npArr = closedf.to_numpy()
# mdd = GetMDD(closedf)
# print(mdd)