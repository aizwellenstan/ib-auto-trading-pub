rootPath = ".."
import sys
sys.path.append(rootPath)
import modules.aiztradingview as aiztradingview
from modules.csvDump import DumpCsv

netIcomeDict = aiztradingview.GetAttr("net_income")
floatSharesDictUS = aiztradingview.GetAttr("float_shares_outstanding")
totalSharesDictUS = aiztradingview.GetAttr("total_shares_outstanding_fundamental")
closeDict = aiztradingview.GetClose()

netIcomeDictJP = aiztradingview.GetAttrJP("net_income")
floatSharesDictJP = aiztradingview.GetAttrJP("float_shares_outstanding")
totalSharesDictJP = aiztradingview.GetAttrJP("total_shares_outstanding_fundamental")
closeDictJP = aiztradingview.GetCloseJP()


netIncomePerShareDict = {}
for symbol, netIncome in netIcomeDict.items():
    floatShares = 0
    if symbol in floatSharesDictUS:
        floatShares = floatSharesDictUS[symbol]
    elif symbol in totalSharesDictUS:
        floatShares = totalSharesDictUS[symbol]
    else: continue
    if symbol not in closeDict: continue
    close = closeDict[symbol]
    if netIncome/floatShares < 0: continue
    netIncomePerShare = netIncome/floatShares/close
    netIncomePerShareDict[symbol] = netIncomePerShare

for symbol, netIncome in netIcomeDictJP.items():
    floatShares = 0
    if symbol in floatSharesDictJP:
        floatShares = floatSharesDictJP[symbol]
    elif symbol in totalSharesDictJP:
        floatShares = totalSharesDictJP[symbol]
    else: continue
    if symbol not in closeDictJP: continue
    close = closeDictJP[symbol]
    if netIncome/floatShares < 0: continue
    netIncomePerShare = netIncome/floatShares/close
    netIncomePerShareDict[symbol] = netIncomePerShare

netIncomePerShareDict = dict(sorted(netIncomePerShareDict.items(), key=lambda item: item[1], reverse=True))
count = 0
newNetIncomePerShareDict = {}
for k, v in netIncomePerShareDict.items():
    newNetIncomePerShareDict[k] = v
    count += 1
    if count > 50: break
print(newNetIncomePerShareDict)

csvPath = f"{rootPath}/data/NetIncome.csv"
DumpCsv(csvPath, list(netIncomePerShareDict.keys()))