import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import pandas as pd
from modules.aiztradingview import GetETF

df = pd.read_csv('us_average_monthly_return.csv')
mon = 'Jul'
df = df.sort_values([mon], ascending=[False])
npArr = df[['Symbol',mon]].head(300).to_numpy()

etf = GetETF()
for i in npArr:
    if i[0] not in etf: continue
    print(i)