from ib_insync import *
import pandas as pd

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)

currency = 'USD'
basicPoint = 0.01

cash = 0
total_cash = 0
def update_balance(*args):
    global cash
    cashDf = pd.DataFrame(ib.accountValues())
    cashDf = cashDf.loc[cashDf['tag'] == 'NetLiquidationByCurrency']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    cash = float(cashDf['value'].iloc[0])
    print(cash)

update_balance()