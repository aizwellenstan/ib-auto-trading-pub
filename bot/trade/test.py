import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
from modules.discord import Alert
import numpy as np
import modules.ib as ibc
from modules.trade.vol import GetVolTp
from modules.normalizeFloat import NormalizeFloat
import math
import sys

ibc = ibc.Ib()
ib = ibc.GetIB(27)
total_cash, avalible_cash = ibc.GetTotalCash()
positions = ibc.GetAllPositions()
basicPoint = 0.01

symbol = "HOTH"

contract = ibc.GetStockContract(symbol)
op = 1
sl = 0.5
tp = 1500
vol = 1
ibc.HandleBuyLimitTpWithContract(contract,vol,op,sl,tp,basicPoint)