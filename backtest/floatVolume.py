rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetAll, GetAttr
from modules.dict import take

symbolList = GetAll()
floatDict = GetAttr("float_shares_outstanding")
volumeDict = GetAttr("average_volume_10d_calc")
industryDict = GetAttr("industry")

noTradeList = ['Pharmaceuticals: Major']
floatVolDict = {}
for symbol in symbolList:
    if symbol not in floatDict: continue
    if symbol not in volumeDict: continue
    industry = industryDict[symbol]
    if industry in noTradeList: continue
    sharesFloat = floatDict[symbol]
    volume = volumeDict[symbol]
    if sharesFloat < 1: continue
    floatVolDict[symbol] = volume/sharesFloat
    
floatVolDict = dict(sorted(floatVolDict.items(), key=lambda item: item[1], reverse=True))
print(take(100,floatVolDict))