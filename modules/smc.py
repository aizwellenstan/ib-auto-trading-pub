import pandas as pd
from smartmoneyconcepts import smc

def GetFvg(npArr):
    df = pd.DataFrame({
            'open': npArr[:,0],
            'high': npArr[:,1],
            'low': npArr[:,2],
            'close': npArr[:,3]
        })
    fvg = smc.fvg(df)
    return fvg.to_numpy()

def GetSwingHighLow(npArr):
    df = pd.DataFrame({
            'open': npArr[:,0],
            'high': npArr[:,1],
            'low': npArr[:,2],
            'close': npArr[:,3]
        })
    swingHighLow = smc.swing_highs_lows(df, 50)
    return swingHighLow

def GetOB(npArr):
    df = pd.DataFrame({
            'open': npArr[:,0],
            'high': npArr[:,1],
            'low': npArr[:,2],
            'close': npArr[:,3],
            'volume': npArr[:,4]
        })
    swingHighLow = smc.swing_highs_lows(df, 50)
    ob = smc.ob(df, swingHighLow, close_mitigation = False)
    return ob.to_numpy()

def GetLiquidity(npArr):
    df = pd.DataFrame({
            'open': npArr[:,0],
            'high': npArr[:,1],
            'low': npArr[:,2],
            'close': npArr[:,3],
            'volume': npArr[:,4]
        })
    swingHighLow = GetSwingHighLow(npArr)
    liquidity = smc.liquidity(df, swingHighLow, range_percent = 0.01)
    return liquidity

def GetBosChoch(npArr):
    df = pd.DataFrame({
            'open': npArr[:,0],
            'high': npArr[:,1],
            'low': npArr[:,2],
            'close': npArr[:,3],
            'volume': npArr[:,4]
        })
    swingHighLow = GetSwingHighLow(npArr)
    bosChoch = smc.bos_choch(df, swingHighLow, close_break = True)
    return bosChoch
# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="365d")

# adx = Adx(df)
# print(adx)