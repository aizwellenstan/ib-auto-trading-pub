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

def gapUp():
    longList = GetMomentum()
    dataDict = {}
    for symbol in longList:
        npArr = GetNpDataShort(symbol, 'USD', True)
        if len(npArr) < 1: continue
        dataDict[symbol] = npArr

    performanceDict = {}
    for key, val in dataDict.items():
        # performance = val[-22][3]/val[-22][0]
        performance = val[-1][3]/val[-2][3]
        performanceDict[key] = performance
    
    performanceDict = dict(sorted(performanceDict.items(), key = lambda x: x[1], reverse = True))
    # Top yesterday gainners
    for key, val in performanceDict.items():
        if dataDict[key][-1][3]>dataDict[key][-2][1]:
            optionChain = haveOptionChain(key)
            print(key, val, optionChain, 'C')
            message = f"gap up {key} {val} {optionChain} C"
            Alert(message)
            break

def gapDown():
    shortList = GetPut()
    dataDict = {}
    for symbol in shortList:
        npArr = GetNpDataShort(symbol, 'USD', True)
        if len(npArr) < 1: continue
        dataDict[symbol] = npArr

    performanceDict = {}
    for key, val in dataDict.items():
        performance = val[-1][3]/val[-2][3]
        performanceDict[key] = performance

    lossPerformanceDict = dict(sorted(performanceDict.items(), key = lambda x: x[1]))
    for key, val in lossPerformanceDict.items():
        if dataDict[key][-1][3]<dataDict[key][-2][2]:
            optionChain = haveOptionChain(key)
            print(key, val, optionChain, 'P')
            message = f"gap down {key} {val} {optionChain} P"
            Alert(message)
            break
    for key, val in lossPerformanceDict.items():
        optionChain = haveOptionChain(key)
        print(key, val, optionChain, 'P')
        message = f"gap down {key} {val} {optionChain} P"
        Alert(message)
        break

def longTernGap():
    longTernList = ['AMZN','UNH','HD','TMO','TD','INTU','ADP',
    'ZTS','NFLX']
    dataDict = {}
    for symbol in longTernList:
        npArr = GetNpDataShort(symbol, 'USD', True)
        if len(npArr) < 1: continue
        dataDict[symbol] = npArr

    performanceDict = {}
    for key, val in dataDict.items():
        # performance = val[-22][3]/val[-22][0]
        performance = val[-1][3]/val[-2][3]
        performanceDict[key] = performance
    
    performanceDict = dict(sorted(performanceDict.items(), key = lambda x: x[1], reverse = True))
    # Top yesterday gainners
    for key, val in performanceDict.items():
        if dataDict[key][-1][3]>dataDict[key][-2][1]:
            optionChain = haveOptionChain(key)
            print(key, val, optionChain, 'C')
            message = f"lontern gap up {key} {val} {optionChain} C"
            Alert(message)
            break

# gapUp()
# gapDown()
longTernGap()