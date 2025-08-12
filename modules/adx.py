import pandas as pd

def get_DM(x):
    if x.prehigh is None:
        return None
    dmpos = x.High - x.prehigh
    dmneg = x.prelow - x.Low
    if dmpos > 0 and dmneg < 0:
        return dmpos
    elif dmpos < 0 and dmneg > 0:
        return -dmneg
    elif (dmpos < 0 and dmneg < 0) or dmpos == dmneg:
        return 0
    elif (x.High == x.Low):
        if dmpos > 0:
            return x.High - x.preclose
        else:
            return -(x.preclose - x.Low)
    else:
        if dmpos > dmneg:
            return dmpos
        else:
            return -dmneg

def get_TR(x):
    if x.prehigh is None:
        return None
    tr1 = abs(x.High - x.Low)
    tr2 = abs(x.High - x.preclose)
    tr3 = abs(x.Low - x.preclose)
    return max([tr1, tr2, tr3])

def Adx(df):
    df_copy = df.copy()
    df_copy['preopen'] = df['Open'].shift(1)
    df_copy['prehigh'] = df['High'].shift(1)
    df_copy['prelow'] = df['Low'].shift(1)
    df_copy['preclose'] = df['Close'].shift(1)

    dm = df_copy.apply(get_DM, axis=1)
    tr = df_copy.apply(get_TR, axis=1)

    dipos = dm.where(dm > 0, 0).rolling(11).mean().abs() / tr.rolling(11).mean()
    dineg = dm.where(dm < 0, 0).rolling(11).mean().abs() / tr.rolling(11).mean()

    adx = ((dipos - dineg).abs() / (dipos + dineg)).ewm(span=4, adjust=False).mean() * 100
    
    return adx

from ta.trend import ADXIndicator
import pandas as pd

def GetADX(npArr):
    df = pd.DataFrame({
            'High': npArr[:,1],
            'Low': npArr[:,2],
            'Close': npArr[:,3]
        })
    adx = ADXIndicator(df['High'], df['Low'],
            df['Close'], 14)
    return adx.adx().to_numpy()

# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="365d")

# adx = Adx(df)
# print(adx)