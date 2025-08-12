rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.csvDump import LoadDict
from modules.aiztradingview import GetCloseJPAll, GetCloseAll, GetAttrAll

rironkabuakaPath = f"{rootPath}/data/Rironkabuka.csv"
symbolMapPath = f"{rootPath}/data/SymbolMapJP.csv"

rironkabakaDict = LoadDict(rironkabuakaPath, 'Rironkabuka')
symbolMapDict = LoadDict(symbolMapPath, 'USSymbol')

closeJPDict = GetCloseJPAll()
closeUSDict = GetCloseAll()

priceUSDict = {}
for symbol, rionkabuka in rironkabakaDict.items():
    # print(str(symbol))
    closeJP = closeJPDict[str(symbol)]
    bairitsu = rionkabuka / closeJP
    if symbol not in symbolMapDict: continue
    USSymbol = symbolMapDict[symbol]
    if USSymbol not in closeUSDict: continue
    closeUS = closeUSDict[USSymbol]
    print(USSymbol,bairitsu)
    priceUS = closeUS * bairitsu
    priceUSDict[USSymbol] = priceUS

print(priceUSDict)

attrCPDict = {}
attrDict = GetAttrAll("total_assets")
for symbol, price in priceUSDict.items():
    attr = attrDict[symbol]
    attrCP = price / attr
    attrCPDict[symbol] = attrCP

# number_of_shareHolders = 0.01582644032832671

attrCPDict = dict(sorted(attrCPDict.items(), key=lambda item: item[1], reverse=True))
print(attrCPDict)