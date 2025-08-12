rootPath = "."
from modules.aiztradingview import GetGrowth

growth = GetGrowth()
import pandas as pd
df = pd.read_csv(f"{rootPath}/data/ib_cfd_us.csv")
cfd = df['Symbol'].values.tolist()


symbolList = [s for s in growth if s in cfd]
cDict = {}
for s, c in growth.items():
    if s in symbolList:
        cDict[s] = c

print(sum(cDict.values())/len(cDict))