rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData
catNpArr = GetNpData('CAT')

catNpArr = GetNpData('CAT')

i = 0

while i > -100:
    if catNpArr[i-1][3] > catNpArr[i-2][3] * 1.05:
        print(i)
    i -= 1