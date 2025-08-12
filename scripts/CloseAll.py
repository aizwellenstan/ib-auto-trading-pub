import sys 
mainFolder = '../..'
sys.path.append(mainFolder)
from modules.discord import Alert
import numpy as np
from modules.trade.vol import GetVolTp
from modules.normalizeFloat import NormalizeFloat
import math
import sys
from modules.trade.placeOrder import PlaceOrder
import pandas as pd
from ib_insync import *

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=38)

# trade = ib.placeOrder(mastercard_contract, mastercard_order)
# if trade.orderStatus.status == 'Filled':
#     ib.disconnect()
#     quit(0)

oriCashDf = pd.DataFrame(ib.accountValues())
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
   print(oriCashDf)

def GetTotalCash():
    oriCashDf = pd.DataFrame(ib.accountValues())
    # cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
    # cashDf = cashDf.loc[cashDf['tag'] == 'AvailableFunds']
    cashDf = oriCashDf.loc[oriCashDf['tag'] == 'NetLiquidationByCurrency']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    total_cash = float(cashDf['value'])
    print(total_cash)
    cashDf = oriCashDf.loc[oriCashDf['tag'] == 'AvailableFunds']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    avalible_cash = float(cashDf['value'])
    print(avalible_cash)
    return total_cash, avalible_cash

def GetAllPositions():
    positions = ib.positions()  # A list of positions, according to IB
    positionList = []
    for position in positions:
        contract = position.contract
        if contract.secType == 'CASH': continue
        positionList.append(contract.symbol)
    return positionList

def closeAll(currency):
    positions = ib.positions()  # A list of positions, according to IB
    for position in positions:
        contract = position.contract
        if contract.strike > 0: continue
        symbol = contract.symbol
        if(symbol in keepOpenList): continue
        if(contract.symbol in closeByMarketList):
            contract = Stock(symbol, 'SMART', currency)
            if position.position > 0: # Number of active Long positions
                action = 'Sell' # to offset the long positions
            elif position.position < 0: # Number of active Short positions
                action = 'Buy' # to offset the short positions
            else:
                assert False
            totalQuantity = abs(position.position)
            order = MarketOrder(action=action, totalQuantity=totalQuantity)
            trade = ib.placeOrder(contract, order)
            print(f'Flatten Position: {action} {totalQuantity} {contract.localSymbol}')
            assert trade in ib.trades(), 'trade not listed in ib.trades'
