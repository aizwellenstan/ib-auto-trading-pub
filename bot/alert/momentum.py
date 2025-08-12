import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
import pandas as pd
import os
import numpy as np
from modules.riskOfRuin import calcRisk
from modules.aiztradingview import GetMomentum, GetPut
from modules.data import GetNpData, GetNpDataShort
from modules.haveOptionChain import haveOptionChain
from modules.discord import Alert

def longMomentum():
    longMomentum = GetMomentum()
    dataDict = {}
    for symbol in longMomentum:
        npArr = GetNpDataShort(symbol, 'USD', True)
        if len(npArr) < 1: continue
        dataDict[symbol] = npArr
    
    performanceDict = {}
    for key, val in dataDict.items():
        performance = val[-1][3]/val[-19][0]
        performanceDict[key] = performance

    performanceDict = dict(sorted(performanceDict.items(), key = lambda x: x[1], reverse = True))

    for key, val in performanceDict.items():
        optionChain = haveOptionChain(key)
        print(key, val, optionChain, 'C')
        message = f"{key} {val} {optionChain} C"
        Alert(message)
        break

def shortMomentum():
    shortMomentum = GetPut()
    dataDict = {}
    for symbol in shortMomentum:
        npArr = GetNpDataShort(symbol, 'USD', True)
        if len(npArr) < 1: continue
        dataDict[symbol] = npArr

    lossPerformanceDict = {}
    for key, val in dataDict.items():
        performance = val[-1][3]/val[-5][0]
        lossPerformanceDict[key] = performance

    lossPerformanceDict = dict(sorted(lossPerformanceDict.items(), key = lambda x: x[1]))
    # Top 3 loser yesterday
    for key, val in lossPerformanceDict.items():
        optionChain = haveOptionChain(key)
        print(key, val, optionChain, 'P')
        message = f"{key} {val} {optionChain} P"
        Alert(message)
        break

def longTernMomentum():
    longTernList = ['AMZN','UNH','HD','TMO']

    dataDict = {}
    for symbol in longTernList:
        npArr = GetNpDataShort(symbol, 'USD', True)
        if len(npArr) < 1: continue
        dataDict[symbol] = npArr
    
    performanceDict = {}
    for key, val in dataDict.items():
        performance = val[-1][3]/val[-6][0]
        performanceDict[key] = performance

    performanceDict = dict(sorted(performanceDict.items(), key = lambda x: x[1], reverse = True))

    for key, val in performanceDict.items():
        optionChain = haveOptionChain(key)
        print(key, val, optionChain, 'C')
        message = f"longTern {key} {val} {optionChain} C"
        Alert(message)
        break

# longMomentum()
# shortMomentum()
# longTernMomentum()