rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.barchart import GetOiChangeStock, GetOiChangeEtf

# npArr = GetOiChangeStock()
# print(npArr)
# print(len(npArr))

npArr = GetOiChangeEtf()
print(npArr)
print(len(npArr))