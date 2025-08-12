import pandas as pd

def get_ichimoku(npArr):
    npArr = npArr[:,:6]
    columns =  ['o', 'h', 'l', 'c', 'vol', 'da']
    df = pd.DataFrame(npArr, columns = columns)
    o = df['o']
    h = df['h']
    l = df['l']
    c = df['c']
    ## 当日を含めた過去26日間の最高値
    ## 当日を含めた過去 9日間の最高値
    ## 当日を含めた過去52日間の最高値
    max26 = h.rolling(window=26).max()
    max9  = h.rolling(window=9).max()
    max52 = h.rolling(window=52).max()
    ## 当日を含めた過去26日間の最安値
    ## 当日を含めた過去 9日間の最安値
    ## 当日を含めた過去52日間の最安値
    min26 = l.rolling(window=26).min()
    min9  = l.rolling(window=9).min()
    min52 = l.rolling(window=52).min()

    ## 基準線=（当日を含めた過去26日間の最高値+最安値）÷2
    ## 転換線=（当日を含めた過去9日間の最高値+最安値）÷2
    kijun = (max26 + min26) / 2
    tenkan = (max9 + min9) / 2
    ## 先行スパン1=｛（転換値+基準値）÷2｝を26日先行させて表示
    senkospan1 = (kijun + tenkan) / 2
    senkospan1 = senkospan1.shift(26)
    ## 先行スパン2=｛（当日を含めた過去52日間の最高値+最安値）÷2｝を26日先行させて表示
    senkospan2 = (max52 + min52) / 2
    senkospan2 = senkospan2.shift(26)
    ## 遅行スパン= 当日の終値を26日遅行させて表示
    chikouspan = c.shift(-26)

    return [kijun, tenkan, senkospan1, senkospan2, chikouspan]