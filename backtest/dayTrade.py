import sys 
mainFolder = '../'
sys.path.append(mainFolder)
import pandas as pd
import os
import numpy as np
from modules.riskOfRuin import calcRisk
from modules.aiztradingview import GetPerformance
from modules.data import GetNpData
from modules.haveOptionChain import haveOptionChain

def backtest(dataDict, bar):
    global spy, qqq
    initialCash = 500
    performanceDict = {}
    daysBack = 167
    for i in range(0, daysBack):
        for key, val in dataDict.items():
            print('QQQ',qqq[-daysBack+i-1][0]/qqq[0][0])
            performance = val[-daysBack+i-1][0]/val[-daysBack+i-1][3]
            performanceDict[key] = performance
    
        performanceDict = dict(sorted(performanceDict.items(), key = lambda x: x[1], reverse = True))
        count = 0
        for key, val in performanceDict.items():
            count += 1
            gain = dataDict[key][-daysBack+i][3]/dataDict[key][-daysBack+i][0]
            initialCash *= gain
            print(key, gain)
            break
    return initialCash

def backtestShort(dataDict, bar):
    initialCash = 500
    performanceDict = {}
    daysBack = 167
    for i in range(0, daysBack):
        for key, val in dataDict.items():
            if len(dataDict[key]) < 300: continue
            performance = val[-daysBack+i-1][3]/val[-daysBack+i-1-bar][0]
            performanceDict[key] = performance
    
        performanceDict = dict(sorted(performanceDict.items(), key = lambda x: x[1]))
        count = 0
        for key, val in performanceDict.items():
            if len(dataDict[key]) < 232: continue
            count += 1
            # if (
            #     dataDict[key][-daysBack+i][0] < dataDict[key][-daysBack+i-1][3]
            # ):
            # if count > 12:
            gain = 2-(dataDict[key][-daysBack+i][3]/dataDict[key][-daysBack+i][0])
            initialCash *= gain
            print(key, gain)
            break
    return initialCash

def Main():
    longTern = GetPerformance()
    dataDict = {}
    spy = GetNpData('SPY', 'USD', False)
    qqq = GetNpData('QQQ', 'USD', False)
    spyPerformance = spy[-1][3]/spy[0][0]
    qqqPerformance = qqq[-1][3]/qqq[0][0]
    print(spyPerformance, qqqPerformance)
    for symbol in longTern:
        npArr = GetNpData(symbol, 'USD', False)
        if (
            npArr[-1][3]/npArr[0][3] > spyPerformance
        ):
            # print(npArr[-1][3],npArr[0][3])
            # print(npArr[-1][3]/npArr[0][0])
            print(symbol)

    
    return 0

Main()