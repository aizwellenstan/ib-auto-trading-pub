import numpy as np
from scipy.stats import linregress
import pandas as pd

def pivotid(df1, l, n1, n2): #n1 n2 before and after candle l
    if l-n1 < 0 or l+n2 >= len(df1):
        return 0
    
    pividlow=1
    pividhigh=1
    for i in range(l-n1, l+n2+1):
        if(df1.low[l]>df1.low[i]):
            pividlow=0
        if(df1.high[l]<df1.high[i]):
            pividhigh=0
    if pividlow and pividhigh:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0
    
def detect_flag(df, candle, backcandles, window, plot_flag=False):
    """
    Attention! window should always be greater than the pivot window! to avoid look ahead bias
    """
    localdf = df[candle-backcandles-window:candle-window]  
    highs = localdf[localdf['pivot'] == 2].high.tail(3).values
    idxhighs = localdf[localdf['pivot'] == 2].high.tail(3).index
    lows = localdf[localdf['pivot'] == 1].low.tail(3).values
    idxlows = localdf[localdf['pivot'] == 1].low.tail(3).index

    if len(highs) == 3 and len(lows) == 3:
        order_condition = ( 
            (idxlows[0] < idxhighs[0] 
            < idxlows[1] < idxhighs[1] 
            < idxlows[2] < idxhighs[2]) 
            or 
            (idxhighs[0] < idxlows[0] 
             < idxhighs[1] < idxlows[1] 
             < idxhighs[2] < idxlows[2]) )
        
        slmin, intercmin, rmin, _, _ = linregress(idxlows, lows)
        slmax, intercmax, rmax, _, _ = linregress(idxhighs, highs)
        
        if (order_condition 
            and (rmax*rmax)>=0.9 
            and (rmin*rmin)>=0.9 
            and slmin>=0.0001 
            and slmax<=-0.0001):
            #and ((abs(slmin)-abs(slmax))/abs(slmax)) < 0.05):

            return 1
    
    return 0

def GetFlag(npArr):
    df = pd.DataFrame(npArr, columns = ['open', 'high', 'low', 'close', 'vol', 'da'])
    df = df[['da', 'open', 'high', 'low', 'close', 'vol']]
    df['low'] = df['low'].astype(float)
    df['high'] = df['high'].astype(float)
    df['pivot'] = df.apply(lambda x: pivotid(df, x.name,3,3), axis=1)
    df['flag'] = df.index.map(lambda x: detect_flag(df, x, 35, 4))
    return df['flag'].values.tolist()