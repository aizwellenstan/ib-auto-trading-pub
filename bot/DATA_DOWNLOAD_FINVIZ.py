rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetCloseAll, GetCloseJP
from modules.data import GetDataWithVolumeDate
from modules.movingAverage import SmaArr
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.threadPool import ThreadPool
import pickle
from modules.loadPickle import LoadPickle
from modules.aizfinviz import GetBSQ, GetCFQ, GetISQ
from modules.dataHandler.bsUS import SaveBS 
from modules.dataHandler.cfUS import SaveCF
from modules.dataHandler.isUS import SaveIS

def HandleGetBSQ(symbol):
    bsq = GetBSQ(symbol)
    return [symbol, bsq]

def HandleGetCFQ(symbol):
    cfq = GetCFQ(symbol)
    return [symbol, cfq]

def HandleGetISQ(symbol):
    isq = GetISQ(symbol)
    return [symbol, isq]

def main():
    closeDictUS = GetCloseAll()
    symbolListUS = list(closeDictUS.keys())

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetBSQ, symbol) for symbol in symbolListUS]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            SaveBS(symbol, res)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetCFQ, symbol) for symbol in symbolListUS]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            SaveCF(symbol, res)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetISQ, symbol) for symbol in symbolListUS]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            SaveIS(symbol, res)

if __name__ == '__main__':
    main()