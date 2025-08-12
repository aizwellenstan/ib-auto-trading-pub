rootPath = ".."
import sys
sys.path.append(rootPath)
import pandas as pd
from numba import range, njit
from datetime import datetime as dt, timedelta
from modules.csvDump import dump_result_list_to_csv
from modules.barchart import GetOiChangeStock, GetOiChangeEtf

def GetData(csvPath):
    df = pd.read_csv(csvPath)
    df = df[['Symbol', 'Price', 'Type', 'Strike', 'Exp Date', 'Ask', 'Open Int', 'OI Chg', 'Volume', 'IV']]
    npArr = df.to_numpy()[:-1]
    return npArr

def Scanner(npArr):
    passedList = []
    ignoreList = ["SQQQ", "VXX"]
    for i in range(0, len(npArr)):
        symbol = npArr[i][0]
        baseSymbol = npArr[i][1]
        if baseSymbol in ignoreList: continue
        baseLastPrice = float(npArr[i][2].replace(",",""))
        baseSymbolType = npArr[i][3]
        symbolType = npArr[i][4]
        try:
            strikePrice = float(npArr[i][5].replace(",",""))
        except: continue
        expirationDate = npArr[i][6]
        daysToExpiration = int(npArr[i][7].replace(",", ""))
        if daysToExpiration <= 0: continue
        if daysToExpiration >= 23: continue
        bidPrice = npArr[i][8]
        midpoint = npArr[i][9]
        askPrice = npArr[i][10]
        lastPrice = npArr[i][11]
        volume = int(npArr[i][12].replace(",",""))
        if volume < 1: continue
        openInterest = int(npArr[i][13].replace(",",""))
        openInterestChange = int(npArr[i][14].replace("+","").replace(",",""))
        volatility = float(npArr[i][15].replace("%",""))
        tradeTime = npArr[i][16]

        previousOi = openInterest - openInterestChange
        if previousOi == 0: continue
        oiChangeToVolume = openInterestChange/volume
        if (
            ((
                symbolType == 'Put' and
                strikePrice > baseLastPrice
            ) or
            (
                symbolType == 'Call' and
                strikePrice < baseLastPrice
            )) and
            volatility > 54.48 and
            oiChangeToVolume > 0.08032378580323786
        ):
            passedList.append([npArr[i],oiChangeToVolume])
    return passedList

# openDate = "2023-06-26"
# openDateTime = dt.strptime(openDate, '%Y-%m-%d')

# npArr = GetData("data/etfs-increase-change-in-open-interest-06-24-2023.csv")
npArr = GetOiChangeEtf()
passedList = Scanner(npArr)
passedList.sort(key=lambda x: x[1], reverse=True)

npArr = GetOiChangeStock()
passedListStock = Scanner(npArr)
passedListStock.sort(key=lambda x: x[1], reverse=True)

passedList += passedListStock

tradeList = []

for i in passedList:
    c = i[0]
    explode = c[0].split("|")
    symbol = explode[0]
    expir = explode[1]
    strike = float(explode[2][0:-1])
    cType = explode[2][-1]
    ask = float(c[10])
    tradeList.append([symbol, expir, strike, cType, ask])

symbol_asks = {}

for entry in tradeList:
    symbol, option_type, ask_price = entry[0], entry[3], entry[4]
    
    if symbol not in symbol_asks:
        symbol_asks[symbol] = float('inf')  # Initialize the smallest ask price as infinity
    
    if ask_price < symbol_asks[symbol]:
        symbol_asks[symbol] = ask_price

filtered_data = [entry for entry in tradeList if entry[4] == symbol_asks[entry[0]]]


symbol_strikes = {}
for entry in filtered_data:
    symbol, strike, option_type, ask_price = entry[0],entry[2], entry[3], entry[4]
    
    if symbol not in symbol_strikes:
        if option_type == "C":
            symbol_strikes[symbol] = float('inf')
        else:
            symbol_strikes[symbol] = 0  # Initialize the smallest ask price as infinity
    
    if strike < symbol_strikes[symbol]:
        symbol_strikes[symbol] = strike

filtered_data = [entry for entry in filtered_data if entry[2] == symbol_strikes[entry[0]] and entry[4]<20.96]

for entry in filtered_data:
    print(entry)

csvPath = f"{rootPath}/data/OIChange.csv"
dump_result_list_to_csv(filtered_data, csvPath, ["Symbol", "Expir", "Strike", "Type", "Ask"])