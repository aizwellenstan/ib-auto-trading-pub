rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose
from modules.data import GetNpData
from modules.get_trend_line import findGrandIntercept
from modules.dict import take
from modules.csvDump import DumpDict

slDict = {}
closeDict = GetClose()
for symbol, close in closeDict.items():
    npArr = GetNpData(symbol)
    if len(npArr) < 624: continue
    npArr = npArr[-624:]
    previews = npArr[:-1]
    lastResistance = findGrandIntercept(previews[:,1])
    lastSupport = findGrandIntercept(previews[:,2])
    resistance = findGrandIntercept(npArr[:,1])
    support = findGrandIntercept(npArr[:,2])

    print(symbol)
    if (
        resistance < lastResistance and
        support > lastSupport
    ):
        sl = support
        if sl > close: continue
        if sl < 0.01: continue
        slDict[symbol] = sl
    print(slDict)

squeezePath = f'{rootPath}/data/Squeeze.csv'
DumpDict(slDict, 'sl', squeezePath)