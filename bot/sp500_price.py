import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.zacks import GetHoldings
from modules.aiztradingview import GetLiquidETF
import yfinance as yf

etfs = GetLiquidETF()
print(etfs)

spy_holdings = GetHoldings("SPY")
spy_holdings = [symbol for symbol in spy_holdings if "." not in symbol]
tickers = etfs + spy_holdings + ["SOXL"]
data = yf.download(tickers, start='2010-11-02')
data.to_parquet(f"{rootPath}/data/prices_SP500.parquet")