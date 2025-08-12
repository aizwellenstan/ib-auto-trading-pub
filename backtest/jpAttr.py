rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetAttrJP

attrDict = GetAttrJP("market_cap_basic")
symbol = '3436'
print(attrDict[symbol])