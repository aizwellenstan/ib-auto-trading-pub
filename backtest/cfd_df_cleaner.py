import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.aiztradingview import GetIndexHoldings, GetLiquidETF
symbolList = list(set(GetIndexHoldings()) | set(GetLiquidETF()))
print(symbolList)
import pandas as pd
df_input = "cfd_dcBreakOut_us_old.csv"
df = pd.read_csv(df_input, index_col=False)
df = df[df['sharpe'] > 0.08]
df = df[df['profitFactor'] > 2.866]
df = df[df['sortino'] > 249]
df = df[~((df['sharpe'] < 0.027) & (df['profitFactor'] <= 4.49))]
df = df[df['symbol'].isin(symbolList)]
df.columns = ["index","symbol", "returns", "sharpe", "sortino", "calmar", "returns_ann", "profitFactor"]
df = df[["symbol", "returns", "sharpe", "sortino", "calmar", "returns_ann", "profitFactor"]]
# print(df[df['symbol'] == 'BLK'])
df.to_csv(df_input)