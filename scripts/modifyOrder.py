from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from logger import log
from datetime import datetime as dt, timedelta
import pandas_datareader.data as web
import numpy as np
from scipy.signal import lfilter
import json
import requests
import talib

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=5)

# oos = list(ib.openOrders())
# print("Orders seen at first")
# for oo in oos:
#     print(f"  order for client {oo.clientId}, id {oo.orderId}, permid {oo.permId}")
# if len(oos) == 0:
#     print("  no order seen")

ib.client.reqAllOpenOrders()  # issue reqAllOpenOrders() directly to IB API, this is a non blocking call
dummy = ib.reqOpenOrders()    # blocking until openOrderEnd messages (may receive two, ib_insync seems not to care
aoos = list(ib.openOrders())  # the orders received from issuing reqAllOpenOrders() are correctly captured
print("\nOrders seen after issuing reqAllOpenOrders()")
for oo in aoos:
    print(f"  order for client {oo.clientId}, id {oo.orderId}, permid {oo.permId}")
    print(vars(oo))
if len(aoos) == 0:
    print("  no order seen")
ib.disconnect()