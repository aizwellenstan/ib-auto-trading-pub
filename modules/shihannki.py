import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import pandas as pd

def SaveShihannki(symbol):
    fPath = f"{rootPath}/data/jp/shihannki/csv/qq-operation-income/{symbol}.csv"
    df = pd.read_csv(fPath)
    print(df)

if __name__ == '__main__':
    SaveShihannki("6315")