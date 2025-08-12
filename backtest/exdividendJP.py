rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.kabumap import GetExdividend
from modules.aiztradingview import GetCloseJPAll
from modules.rironkabuka import GetRironkabuka

# dividendPercentage > 5.56
closeJPDict = GetCloseJPAll()
exdividendDict = GetExdividend()
exdividendList = exdividendDict[next(iter(exdividendDict.keys()))]
passedList = []
for symbol in exdividendList:
    close = closeJPDict[symbol]
    rironkabuka = GetRironkabuka(symbol)
    if close > rironkabuka: continue
    print(symbol, rironkabuka, close)
    passedList.append(symbol)
print(passedList)
