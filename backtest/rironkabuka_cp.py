rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetCloseJP
from modules.rironkabuka import GetRironkabuka
from modules.csvDump import DumpCsv

cheapDict = {}
closeDict = GetCloseJP()
for symbol, close in closeDict.items():
    rironkabuka = GetRironkabuka(symbol)
    if close < rironkabuka:
        cheapDict[symbol] = rironkabuka/close
        print(symbol,close,rironkabuka)
cheapDict = dict(sorted(cheapDict.items(), key=lambda item: item[1], reverse=True))
resPath = f"{rootPath}/data/CheapCP.csv"
cheapList = cheapDict.keys()
print(cheapList)
DumpCsv(resPath,cheapList)