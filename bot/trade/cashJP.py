rootPath = "../..";import sys;sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.csvDump import DumpCsv, dump_result_list_to_csv, load_csv_rows
from numba import range
import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(4)


avalible_cash = ibc.GetAvailableCash() - 1737
avalible_price = int(avalible_cash)/100
print(avalible_price)

positions = ibc.GetAllPositions()


def main(update=True):
    cashPath = f"{rootPath}/data/CashJP.csv"
    cashList = load_csv_rows(cashPath)

    for c in cashList:
        symbol = c[0]
        if symbol in positions: continue
        ibc.HandleBuyLimitTrail(symbol, 100)
        

if __name__ == "__main__":
    update = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'false':
            update = False
    main(update)
