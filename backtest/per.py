import sys
rootPath = '..'
sys.path.append('..')
from modules.aiztradingview import GetAttr
from modules.data import GetDf

profitDict = GetAttr("Performance.All")
floatDict = GetAttr("float_shares_outstanding")

perDict = {}
for symbol, profit in profitDict.items():
    if symbol not in floatDict: continue
    sharesFloat = floatDict[symbol]
    if sharesFloat < 1: continue
    per = profit/sharesFloat
    perDict[symbol] = per

perDict = dict(sorted(perDict.items(), key=lambda item: item[1], reverse=True))
newPerDict = {}
count = 0
for symbol, per in perDict.items():
    newPerDict[symbol] = per
    count += 1
    if count > 20: break
print(newPerDict)