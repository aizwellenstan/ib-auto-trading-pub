import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.irbank import GetLending, GetZandaka, \
    GetNisshokin, GetCategories, \
    GetShort, GetMargin, \
    GetOfficerHold, \
    GetChart, \
    GetPlbscfdividend, GetSegment, \
    GetSafety, GetEmployee, GetQuarter, \
    GetCapex, GetBS, GetHolder
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import numpy as np
from modules.loadPickle import LoadPickle
from modules.dataHandler.category import SaveCategories
from modules.dataHandler.chart import SaveChart
from modules.dataHandler.capex import SaveCapex
from modules.dataHandler.bs import SaveBS
from modules.dataHandler.lending import SaveLending
from modules.dataHandler.zandaka import SaveZandaka
from modules.dataHandler.nisshokin import SaveNisshokin
from modules.dataHandler.quarter import SaveQuarter
from modules.dataHandler.short import SaveShort
from modules.dataHandler.dividend import SaveDividend
from modules.dataHandler.holder import SaveHolder

# symbol = '3382'
# quarter = GetQuarter(symbol)
# print(quarter)
# SaveQuarter(symbol, quarter)
# sys.exit()

def HandleGetLending(symbol):
    lending = GetLending(symbol)
    return [symbol, lending]

def HandleGetZandaka(symbol):
    zandaka = GetZandaka(symbol)
    return [symbol, zandaka]

def HandleGetNisshokin(symbol):
    nisshokin = GetNisshokin(symbol)
    return [symbol, nisshokin]

def HandleGetQuarter(symbol):
    quarter = GetQuarter(symbol)
    return [symbol, quarter]

def HandleGetChart(symbol):
    chart = GetChart(symbol)
    return [symbol, chart]

def HandleGetCapex(symbol):
    capex = GetCapex(symbol)
    return [symbol, capex]

def HandleGetBS(symbol):
    bs = GetBS(symbol)
    return [symbol, bs]

def HandleGetShort(symbol):
    short = GetShort(symbol, da)
    return [symbol, short]

def HandleGetMargin(symbol):
    margin = GetMargin(symbol)
    return [symbol, margin]

def HandleGetHolder(symbol):
    holder = GetHolder(symbol)
    return [symbol, holder]

def HandleGetOfficerHold(symbol):
    officerHold = GetOfficerHold(symbol)
    return [symbol, officerHold]

def HandleGetPlbscfdividend(symbol):
    plbscfdividend = GetPlbscfdividend(symbol)
    return [symbol, plbscfdividend]

def HandleGetSegment(symbol):
    segment = GetSegment(symbol)
    return [symbol, segment]

def HandleGetChart(symbol):
    chart = GetChart(symbol)
    return [symbol, chart]

def HandleGetEmployee(symbol):
    employee = GetEmployee(symbol)
    return [symbol, employee]

def HandleGetSafety(symbol):
    safety = GetSafety(symbol)
    return [symbol, safety]

def main():
    zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
    shortPath = f"{rootPath}/backtest/pickle/pro/compressed/short.p"
    marginPath = f"{rootPath}/backtest/pickle/pro/compressed/margin.p"
    officerHoldPath = f"{rootPath}/backtest/pickle/pro/compressed/officerHold.p"
    chartPath = f"{rootPath}/backtest/pickle/pro/compressed/chart.p"
    shortBasePath = f"{rootPath}/backtest/pickle/pro/compressed/shortBase.p"
    plbscfdividendPath = f"{rootPath}/backtest/pickle/pro/compressed/plbscfdividend.p"
    segmentPath = f"{rootPath}/backtest/pickle/pro/compressed/segment.p"
    employeePath = f"{rootPath}/backtest/pickle/pro/compressed/employee.p"
    safetyPath = f"{rootPath}/backtest/pickle/pro/compressed/safety.p"

    categories = GetCategories()
    print(categories)
    SaveCategories(categories)
    symbolList = categories[:, 0]

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetShort, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            symbol = result[0]
            short = result[1]
            if len(short) < 1: continue
            SaveShort(symbol, short)

    try:
        plbscfdividendDict = LoadPickle(plbscfdividendPath)
    except: plbscfdividendDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetPlbscfdividend, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            plbscfdividend = result[1]
            if len(plbscfdividend) < 1: continue
            plbscfdividendDict[symbol] = plbscfdividend
    if len(plbscfdividendDict) > 0:
        pickle.dump(plbscfdividendDict, open(plbscfdividendPath, "wb"))
        print("pickle dump finished")

    for symbol, plbscfdividend in plbscfdividendDict.items():
        dividend = plbscfdividend[3]
        if len(dividend) < 1: continue
        if len(dividend[0]) in [3, 4, 6, 7]:
            continue
        res = []
        for i in dividend:
            if "予" in i[0]: continue
            da = i[0]
            ichikabuhaitou = i[1]
            if "*" in str(i[1]) or  ichikabuhaitou == "-": 
                ichikabuhaitou = 0
            
            data = [da, ichikabuhaitou]
            res.append(data)
        SaveDividend(symbol, res)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetNisshokin, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            SaveNisshokin(symbol, res)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetZandaka, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            SaveZandaka(symbol, res)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetChart, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            SaveChart(symbol, res)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetQuarter, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            symbol = result[0]
            res = result[1]
            if len(res) < 1: continue
            SaveQuarter(symbol, res)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetHolder, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            symbol = result[0]
            holder = result[1]
            if len(holder) < 1: continue
            SaveHolder(symbol, holder)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetCapex, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            SaveCapex(symbol, res)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetBS, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            SaveBS(symbol, res)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetLending, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            SaveLending(symbol, res)

    chartDict = LoadPickle(chartPath)
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetChart, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            chart = result[1]
            if len(chart) < 1: continue
            chartDict[symbol] = chart
    pickle.dump(chartDict, open(chartPath, "wb"))
    print("pickle dump finished")

    # shortBaseDict = {}
    # shortDict = LoadPickle(shortPath)
    # with ThreadPoolExecutor(max_workers=100) as executor:
    #     futures = [executor.submit(HandleGetShort, symbol) for symbol in symbolList]
    #     for future in as_completed(futures):
    #         result = future.result()
    #         if len(result) < 1: continue
    #         symbol = result[0]
    #         shortBase = result[1]
    #         short = result[2]
    #         if len(short) < 1: continue
    #         shortBaseDict[symbol] = shortBase
    #         shortDict[symbol] = short
    # pickle.dump(shortBaseDict, open(shortBasePath, "wb"))
    # print("pickle dump finished")
    # pickle.dump(shortDict, open(shortPath, "wb"))
    # print("pickle dump finished")

    officerHoldDict = LoadPickle(officerHoldPath)
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetOfficerHold, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            officerHold = result[1]
            if len(officerHold) < 1: continue
            officerHoldDict[symbol] = officerHold
    pickle.dump(officerHoldDict, open(officerHoldPath, "wb"))
    print("pickle dump finished")

    employeeDict = LoadPickle(employeePath)
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetEmployee, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            employee= result[1]
            if len(employee) < 1: continue
            employeeDict[symbol] = employee
    pickle.dump(employeeDict, open(employeePath, "wb"))
    print("pickle dump finished")

    safetyDict = LoadPickle(safetyPath)
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetSafety, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            safety= result[1]
            if len(safety) < 1: continue
            safetyDict[symbol] = safety
    pickle.dump(safetyDict, open(safetyPath, "wb"))
    print("pickle dump finished")

    marginDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetMargin, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            margin = result[1]
            if len(margin) < 1: continue
            marginDict[symbol] = margin
    if len(marginDict) > 0:
        pickle.dump(marginDict, open(marginPath, "wb"))
        print("pickle dump finished")

    segmentDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetSegment, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            segment= result[1]
            if len(segment) < 1: continue
            segmentDict[symbol] = segment
    pickle.dump(segmentDict, open(segmentPath, "wb"))
    print("pickle dump finished")

if __name__ == '__main__':
    main()