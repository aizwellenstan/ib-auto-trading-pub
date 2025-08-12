rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetCloseJP, GetAttrJP
from modules.rironkabuka import GetRironkabuka
from modules.margin import GetMargin, GetUSStock
from modules.csvDump import DumpCsv, DumpDict, LoadDict
from modules.dict import take
import pandas as pd
# from modules.irbank import GetZandaka

rironkabuakaPath = f"{rootPath}/data/Rironkabuka.csv"

rironkabukaDict = {}
shinyouzanDict = {}
closeDict = GetCloseJP()
attrDict = GetAttrJP("float_shares_outstanding")
for symbol, close in closeDict.items():
    rironkabuka = GetRironkabuka(symbol)
    rironkabukaDict[symbol] = rironkabuka
    if close < rironkabuka:
        rironkabukaDict[symbol] = rironkabuka
        margin = GetMargin(symbol)
        if len(margin) < 1: continue
        # urizan = margin[0][0]
        # kaizan = margin[0][1]
        # shinyoubairitsu = margin[0][4]
        # if marginTransactionSellFluctuation < -125299: continue
        # 売残 買残 売残増減 買残増減 信用倍率 日付
        if margin[0][2] < 0: continue
        diff = margin[0][2] - margin[0][3]
        if diff <= 0: continue
        if symbol not in attrDict: continue
        sharesFloat = attrDict[symbol]
        # zandaka = GetZandaka(symbol)
        # if len(zandaka) < 1: continue
        # shorts = zandaka[0][4]
        # diffPercentage = shorts/sharesFloat
        diffPercentage = diff/sharesFloat
        print(diffPercentage)
        shinyouzanDict[symbol] = diffPercentage

DumpDict(rironkabukaDict,'Rironkabuka',rironkabuakaPath)
shinyouzanDict  = dict(sorted(shinyouzanDict .items(), key=lambda item: item[1]))
shinyouzanList = take(len(shinyouzanDict),shinyouzanDict)
print(shinyouzanDict)
print(shinyouzanList)
resPath = f"{rootPath}/data/Shinyouzan.csv"
DumpCsv(resPath,shinyouzanList)

symbolMapPath = f"{rootPath}/data/SymbolMapJP.csv"
symbolMapDictJP = LoadDict(symbolMapPath, 'USSymbol')
for symbol in closeDict.keys():
    if symbol not in symbolMapDictJP:
        usSymbol = GetUSStock(symbol)
        if len(usSymbol) < 1: continue
        symbolMapDictJP[symbol] = usSymbol
DumpDict(symbolMapDictJP, 'USSymbol', symbolMapPath)

sinyouZanUSPath = f"{rootPath}/data/ShinyouzanUS.csv"
shinyouzanUSDict = {}
for symbol in shinyouzanList:
    if symbol in symbolMapDictJP:
        usSymbol = symbolMapDictJP[symbol]
    else:
        usSymbol = GetUSStock(symbol)
        if usSymbol == "": continue
    print(symbol,usSymbol)
    shinyouzanUSDict[symbol] = usSymbol
DumpDict(shinyouzanUSDict,'USSymbol',sinyouZanUSPath)