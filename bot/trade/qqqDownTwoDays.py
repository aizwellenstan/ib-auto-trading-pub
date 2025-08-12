import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from ib_insync import Stock, CFD
from modules.trade.options import BuyOption
from config import load_credentials
from modules.trade.futures import ExecTrail
ACCOUNT = load_credentials('account')
STOCKACCOUNT = load_credentials('stockAccount')
CASHACCOUNT = load_credentials('cashAccount')

ibc = ibc.Ib()
ib = ibc.GetIB(1)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
# total_cash *= 4 # margin
total_cash /= 2
print(total_cash)

stock_total_cash, stock_avalible_cash = ibc.GetTotalCash(STOCKACCOUNT)
stock_total_cash /= 2

def main():
    contractQQQ = Stock("QQQ", 'SMART', 'USD')
    contractNVDA = Stock("NVDA", 'SMART', 'USD')
    contractNVDACFD = CFD("NVDA", 'SMART', 'USD')
    contractSMH = Stock("SMH", 'SMART', 'USD')
    npArr = ibc.GetDataNpArr(contractQQQ, '1 day', useRTH=True)
    if not (
        npArr[-2][3] < npArr[-2][0] and
        npArr[-1][3] < npArr[-1][0]
    ): return 0
    Alert("QQQ DOWN 2 Days")
    sys.exit()
    # Buy NVDA Option With 0.5 cent Trail
    try:
        chains = ibc.GetChains("NVDA")
        closeNVDA = ibc.GetDataNpArr(contractNVDA, '1 min')[-1][3]
        BuyOption(ib, ibc, 'NVDA', chains, 1, 1, closeNVDA, 0.5, CASHACCOUNT)
    except: pass

    # # Buy NVDA Stock
    # vol = int(stock_total_cash / closeNVDA)
    # op = closeNVDA + 0.5
    # sl = closeNVDA - 2.95
    # tp = closeNVDA * 10
    # ExecTrail(ibc, 1, contractNVDACFD, vol, op, sl, tp, 0.01, True, CASHACCOUNT)
main()