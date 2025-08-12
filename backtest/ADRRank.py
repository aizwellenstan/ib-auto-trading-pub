rootPath = ('../')
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetADRRank

adrDict = GetADRRank()
print(adrDict)

adrList = []
for k, v in adrDict.items():
    adrList.append(k)
print(adrList[:100])