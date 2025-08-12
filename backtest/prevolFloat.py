import sys
mainFolder = '../'
sys.path.append(mainFolder)
from modules.aiztradingview import GetPreVolFloat, GetShares

prevolFloatDict = GetPreVolFloat('USD')

print(prevolFloatDict['F'])
print(prevolFloatDict['HUT'])

floatDict = GetShares('USD')
floatDWAC = floatDict['DWAC']
floatPHUN = floatDict['PHUN']
floatBKKT = floatDict['BKKT']

print(34264405/floatDWAC)
print(139606054/floatPHUN)
print(5769837/floatBKKT)

import alpaca_trade_api as tradeapi
api = tradeapi.REST(,
                    secret_key="",
                    base_url='https://paper-api.alpaca.markets')
shortable_list = [l for l in api.list_assets() if l.shortable]


shortableSymList = []
for sym in shortable_list:
    shortableSymList.append(sym.symbol)

print(shortableSymList)

if "F" in shortableSymList:
    print("F")

if "HUT" in shortableSymList:
    print("HUT")