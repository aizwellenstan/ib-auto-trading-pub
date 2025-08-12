rootPath = "../..";import sys;sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.csvDump import DumpCsv, dump_result_list_to_csv, load_csv_rows
from numba import range
import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(5)

avalible_cash = ibc.GetAvailableCash()
avalible_price = int(avalible_cash)
print(avalible_price)

positions = ibc.GetAllPositions()

def main(update=True):
    csvPath = f"{rootPath}/data/ScannerUS.csv"
    symbolList = load_csv_rows(csvPath)

    for c in symbolList:
        if float(c[1]) > avalible_price: continue
        symbol = c[0]
        if symbol in positions: continue
        vol = int(avalible_cash/2/float(c[1]))
        ibc.HandleBuyLimitTpTrail(symbol, vol)
        print(symbol,vol)

if __name__ == "__main__":
    update = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'false':
            update = False
    main(update)
