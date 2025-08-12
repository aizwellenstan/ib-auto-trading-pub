rootPath = "../..";import sys;sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.csvDump import DumpCsv, dump_result_list_to_csv, load_csv_rows
from numba import range
import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(11)

avalible_cash = ibc.GetAvailableCash()
avalible_price = int(avalible_cash)/100
print(avalible_price)

positions = ibc.GetAllPositions()

def main(update=True):
    tradeList = []
    csvPath = f"{rootPath}/data/ScannerJP.csv"
    symbolList = load_csv_rows(csvPath)

    count = 0
    for c in symbolList:
        count += 1
        # if count > 4: break
        symbol = c[0]
        if symbol in positions: break
        if float(c[1]) > avalible_price: continue
        ibc.HandleBuyLimitTpTrail(symbol, 100)
        tradeList.append(symbol)
        break
        

    # valuePath = f"{rootPath}/data/ValueJP.csv"
    # valueList = load_csv_rows(valuePath)

    # for c in valueList:
    #     symbol = c[0]
    #     if symbol in positions: continue
    #     if symbol in tradeList: continue
    #     if float(c[2]) > avalible_price: continue
    #     ibc.HandleBuyLimitTrail(symbol, 100)
    #     tradeList.append(symbol)
    #     break

    # roePath = f"{rootPath}/data/RoeJP.csv"
    # roeList = load_csv_rows(roePath)

    # for c in roeList:
    #     symbol = c[0]
    #     if symbol in positions: continue
    #     if symbol in tradeList: continue
    #     if float(c[2]) > avalible_price: continue
    #     ibc.HandleBuyLimitTrail(symbol, 100)
    #     tradeList.append(symbol)
    #     break

if __name__ == "__main__":
    update = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'false':
            update = False
    main(update)
