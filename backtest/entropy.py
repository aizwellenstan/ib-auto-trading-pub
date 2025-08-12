import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import modules.ib as ibc
from modules.trade.futures import GetFuturesContracts
from modules.entropy import generate_signal, CheckSignal
from ib_insync import *

ibc = ibc.Ib()
ib = ibc.GetIB(6)

contractES, contractNQ, contractMNQ, contractMES, contractTOPX, contractMNTPX, contractMCL, contractN225, contractN225M, contractN225MC, contractMHI, contractDJIA, contractMGC,  contractJPY, contractNKD = GetFuturesContracts(ib)

contract = Stock("XLE", "SMART", "USD")
ib.reqMktData(contract, '', False, False)

# ticker = ib.ticker(contractES)
# ib.sleep(2)

ma_val, en_val, en_ma_val = 0, 0, 0
def onPendingTickers(tickers):
    for t in tickers:
        # , t.high, t.low, t.close
        print(
            t.bidSize, t.bid, t.ask, t.askSize)
        print(t.contract.symbol)
        entropy_signal = CheckSignal(t.bidSize, t.askSize, t.close, ma_val, en_val, en_ma_val)
ib.pendingTickersEvent += onPendingTickers

lastMinute = 0
while(ib.sleep(2)):
    currentTime = ib.reqCurrentTime()
    if currentTime.minute != lastMinute:
        npArr = ibc.GetDataNpArr(contract, '1 min')
        ma_val, en_val, en_ma_val = generate_signal(npArr[:-1][:,3][-109:])
        lastMinute = currentTime.minute
# signal = generate_signal(npArr[:-1][:,3][-109:])
# print(f"Trading Signal: {signal}")
