rootPath = ".."
import sys
sys.path.append(rootPath)
import pandas as pd
from numba import range, njit
from datetime import datetime as dt, timedelta
from modules.csvDump import dump_result_list_to_csv

def GetData(csvPath):
    df = pd.read_csv(csvPath)
    df = df[['Symbol', 'Price', 'Type', 'Strike', 'Exp Date', 'Ask', 'Open Int', 'OI Chg', 'Volume', 'IV']]
    npArr = df.to_numpy()[:-1]
    return npArr

def Scanner(passedList, npArr):
    for i in range(0, len(npArr)):
        oiChange = int(npArr[i][7].replace("+","").replace(",",""))
        previousOi = npArr[i][6] - oiChange
        iv = float(npArr[i][9].replace("%",""))
        if previousOi == 0: continue
        if (
            ((
                npArr[i][2] == 'Put' and
                npArr[i][3] > npArr[i][1]
            ) or
            (
                npArr[i][2] == 'Call' and
                npArr[i][3] < npArr[i][1]
            )) and
            iv > 54.48 and
            oiChange/npArr[i][8] > 0.08032378580323786
        ):
            time = dt.strptime(npArr[i][4], '%Y-%m-%d')
            diff = time - openDateTime
            if diff <= timedelta(days=0): continue
            if diff >= timedelta(days=23): continue
            # passedList.append([npArr[i],npArr[i][6]/previousOi])
            passedList.append([npArr[i],oiChange/npArr[i][8]])
    return passedList

openDate = "2023-06-25"
openDateTime = dt.strptime(openDate, '%Y-%m-%d')

npArr = GetData("data/etfs-increase-change-in-open-interest-06-24-2023.csv")
passedList = Scanner([], npArr)
passedList.sort(key=lambda x: x[1], reverse=True)
# print(passedList)

npArr = GetData("data/stocks-increase-change-in-open-interest-06-24-2023.csv")
passedListStock = Scanner([], npArr)
passedListStock.sort(key=lambda x: x[1], reverse=True)
# print(passedListStock)

passedList += passedListStock

tradeList = []

for i in passedList:
    c = i[0]
    symbol = c[0]
    expir = c[4].replace("-","")
    strike = c[3]
    cType = "C" if c[2] == "Call" else "P"
    tradeList.append([symbol, expir, strike, cType])
# print(tradeList)

# filtered_data = {}

# for entry in tradeList:
#     symbol, expir, strike, option_type = entry[0], entry[1], entry[2], entry[3]
    
#     key = (symbol, expir)
#     if key not in filtered_data:
#         filtered_data[key] = []
    
#     filtered_data[key].append((strike, option_type))

# final_data = []
# for key, options in filtered_data.items():
#     symbol, expir = key[0], key[1]
    
#     calls = [(strike, option_type) for strike, option_type in options if option_type == "C"]
#     puts = [(strike, option_type) for strike, option_type in options if option_type == "P"]
    
#     # if calls:
#     #     max_strike = max(calls, key=lambda x: x[0])[0]
#     #     final_data.append([symbol, expir, max_strike, "C"])
    
#     # if puts:
#     #     min_strike = min(puts, key=lambda x: x[0])[0]
#     #     final_data.append([symbol, expir, min_strike, "P"])

#     if calls and not puts:
#         max_strike = max(calls, key=lambda x: x[0])[0]
#         final_data.append([symbol, expir, max_strike, "C"])
    
#     if puts and not calls:
#         min_strike = min(puts, key=lambda x: x[0])[0]
#         final_data.append([symbol, expir, min_strike, "P"])

# for entry in final_data:
#     print(entry)

symbol_expir_mapping = {}
final_data = []

for entry in tradeList:
    symbol, expir, strike, option_type = entry[0], entry[1], entry[2], entry[3]
    
    if symbol not in symbol_expir_mapping:
        symbol_expir_mapping[symbol] = set()
    
    symbol_expir_mapping[symbol].add(expir)

for entry in tradeList:
    symbol, expir, strike, option_type = entry[0], entry[1], entry[2], entry[3]
    
    if symbol in symbol_expir_mapping and len(symbol_expir_mapping[symbol]) == 1:
        final_data.append(entry)

for entry in final_data:
    print(entry)

csvPath = f"{rootPath}/data/OIChange.csv"
dump_result_list_to_csv(final_data, csvPath, ["Symbol", "Expir", "Strike", "Type"])