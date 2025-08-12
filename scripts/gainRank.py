from modules.data import GetNpData
from modules.aiztradingview import GetDividends

benchmark = 0.1462602936447545

dividends = GetDividends()

dividends = ['DHCNL', 'SU', 'AMZN']
noTradeList = []
gainDict = {}
for symbol in dividends:
    npData = GetNpData(symbol)
    if len(npData) < 1: continue
    gain = npData[-1][3] / npData[0][0]
    gainSpeed = gain/len(npData)
    if gainSpeed < 0.1462602936447545:
        noTradeList.append(symbol)
        continue
    gainDict[symbol] = gainSpeed
    print(gainSpeed)

print(noTradeList)
gainDict = dict(sorted(gainDict.items(), key=lambda item: item[1], reverse=True))
gainList = []
print(gainDict)
for k, v in gainDict.items():
    gainList.append(k)
print(gainList)