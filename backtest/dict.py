rootPath = "..";import sys;sys.path.append(rootPath)
from modules.dict import take

dataDict = {"9101": 200}
data = take(10, dataDict)
print(data)