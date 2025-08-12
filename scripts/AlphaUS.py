rootPath = "."
from modules.aiztradingview import GetAlphaUS

growth = GetAlphaUS()
import pandas as pd
df = pd.read_csv(f"{rootPath}/data/ib_cfd_us.csv")
cfd = df['Symbol'].values.tolist()


symbolList = [s for s in growth if s in cfd]
print(symbolList)