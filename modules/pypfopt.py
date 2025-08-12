import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import expected_returns, risk_models

def handleData(dataDict, symbolList, i):
    df = pd.DataFrame()
    for symbol in symbolList:
        temp_df = pd.DataFrame(dataDict[symbol][:i], columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Date'])
        temp_df = temp_df[['Close', 'Date']]
        temp_df['Date'] = pd.to_datetime(temp_df['Date'])
        temp_df.set_index('Date', inplace=True)
        temp_df.rename(columns={'Close': symbol}, inplace=True)
        if df.empty:
            df = temp_df
        else:
            df = df.join(temp_df, how='outer')
    df.sort_index(inplace=True)
    return df

def GetMaxSRV2(dataDict, symbolList, i):
    df = handleData(dataDict, symbolList, i)
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    ef = EfficientFrontier(mu, S)
    try:
        weights = ef.max_sharpe()
    except: return {}
    return weights
    # return {key: value for key, value in weights.items() if value > 0}

def GetMinVol(dataDict, symbolList, i):
    df = handleData(dataDict, symbolList, i)
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    ef = EfficientFrontier(mu, S)
    try:
        # ef.min_volatility()
        weights = ef.efficient_risk(0.03)
    except: return {}
    return weights

def GetEfficientRisk(dataDict, symbolList, i):
    df = handleData(dataDict, symbolList, i)
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    ef = EfficientFrontier(mu, S)
    try:
        weights = ef.efficient_risk()
    except: return {}
    return weights
    return {key: value for key, value in weights.items() if value > 0}