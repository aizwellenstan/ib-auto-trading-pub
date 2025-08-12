rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.margin import GetUSStock
import os
import pandas as pd

def dumpDict(dataDict, path):
    if len(dataDict) > 1:
        df = pd.DataFrame()
        df['Symbol'] = dataDict.keys()
        df['USSymbol'] = dataDict.values()
        df.to_csv(path)

shinyouzanList = []
sinyouZanPath = f"{rootPath}/data/Shinyouzan.csv"
if os.path.exists(sinyouZanPath):
    df = pd.read_csv(sinyouZanPath)
    shinyouzanList = list(df.Symbol.values)

sinyouZanUSPath = f"{rootPath}/data/ShinyouzanUS.csv"
shinyouzanUSDict = {}
for symbol in shinyouzanList:
    usSymbol = GetUSStock(symbol)
    if usSymbol == "": continue
    shinyouzanUSDict[symbol] = usSymbol
    dumpDict(shinyouzanUSDict,sinyouZanUSPath)