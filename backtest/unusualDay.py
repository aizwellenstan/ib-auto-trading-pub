import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.holdings import GetHoldings
from modules.data import GetDf

df = GetDf('QQQ')
print(df.iloc[-1].Close/df.iloc[-1].Open)

for i in range(0, len(df)):
    rangeD = df.iloc[i].Close/df.iloc[i].Open
    if rangeD < 0.97:
        print(df.iloc[i].Date)