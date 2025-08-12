rootPath = "..";import sys;sys.path.append(rootPath)
from modules.data import GetNpDataLts
from modules.data import GetExDividendTime

symbol = "ARKO"
dividend = GetExDividendTime(symbol)
print(dividend)