rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose, GetAttr
from modules.portfolio import GetData
from modules.csvDump import DumpDict

closeDict = GetClose()
print(closeDict)
attrDict = GetAttr("industry")

cagrDict = {}
for symbol, close in closeDict.items():
    npArr = GetData(symbol)
    if len(npArr) < 1: continue
    cagr = npArr[0][3]
    cagrDict[symbol] = cagr
    print(symbol, cagr)

cagrDict = dict(sorted(cagrDict.items(), key=lambda item: item[1], reverse=True))
cagrList = list(cagrDict.keys())

resDict = {}
for symbol in cagrList:
    if symbol not in attrDict: continue
    resDict[symbol] = attrDict[symbol]

resPath = f"{rootPath}/data/CAGR.csv"
DumpDict(resDict, "Industry", resPath)