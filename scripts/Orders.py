from ib_insync import *
import numpy as np
import pandas as pd
import math
from typing import NamedTuple
import sys
sys.path.append('.')

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)
def cancelUntriggered(action = "SELL"):
    openTrades = ib.openTrades()
    print(openTrades)
    # oos = list(ib.openOrders())
    # ib.client.reqAllOpenOrders()  # issue reqAllOpenOrders() directly to IB API, this is a non blocking call
    # dummy = ib.reqOpenOrders()    # blocking until openOrderEnd messages (may receive two, ib_insync seems not to care
    # aoos = list(ib.openOrders())  # the orders received from issuing reqAllOpenOrders() are correctly captured
    
    # for oo in aoos:
    #     if oo.orderType == "TRAIL":
    #         if oo.action == action:
    #             print(oo.stockRefPrice)
        # if oo.orderType == "LMT":
        #     if oo.action == action:
        #         print(oo.tuple)
        # if oo.orderType != "TRAIL": continue
        # print(f"  order for client {oo.clientId}, id {oo.orderId}, permid {oo.permId}")
        # print(oo.trailStopPrice)

cancelUntriggered()