import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

def Decompose(npArr):
    df = pd.DataFrame({
        'da': npArr[:,5],
        'cl': npArr[:,3]
    })
    df['da'] = pd.to_datetime(df['da'])
    df.set_index('da', inplace=True)
    result = seasonal_decompose(df, 
                                model='multiplicative', 
                                period=252, 
                                extrapolate_trend='freq', 
                                two_sided=False)
    trend = result.trend.to_numpy()
    seasonal = result.seasonal.to_numpy()
    residual = result.resid.to_numpy()
    return [trend, seasonal, residual]

def DecomposeDf(df):
    df.set_index('da', inplace=True)
    result = seasonal_decompose(df, 
                                model='multiplicative', 
                                period=48, 
                                extrapolate_trend='freq', 
                                two_sided=False)
    trend = result.trend.to_numpy()
    seasonal = result.seasonal.to_numpy()
    residual = result.resid.to_numpy()
    return [trend, seasonal, residual]