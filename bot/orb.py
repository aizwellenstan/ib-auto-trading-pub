import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import numpy as np
from modules.loadPickle import LoadPickle
from modules.atr import ATR

def main():
    dataPath = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
    dataDict = LoadPickle(dataPath)

    import pandas as pd
    df = pd.read_csv(f"{rootPath}/data/ib_cfd_us.csv")
    cfd = df['Symbol'].values.tolist()

    symbolList = []
    for symbol, npArr in dataDict.items():
        if symbol not in cfd: continue
        volArr = npArr[-14:][:,4]
        rv = np.mean(volArr)
        if rv <= 1000000: continue
        npArr = npArr[-15:]
        atr = ATR(npArr[:,1],npArr[:,2],npArr[:,3],14)
        if atr <= 0.5: continue
        symbolList.append([symbol, atr])
    df = pd.DataFrame(symbolList)
    df.columns = ["Symbol", "Atr"]
    df.to_csv(f"{rootPath}/data/orb.csv")
main()