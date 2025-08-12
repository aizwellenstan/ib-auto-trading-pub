import json
import redis
from modules.discord import Alert
import modules.ib as ibc
from config import load_credentials
from modules.trade.futures import GetFuturesContracts, ExecBracket

ACCOUNT = load_credentials('futuresAccount')
ibc = ibc.Ib()
ib = ibc.GetIB(1)
contractDict = GetFuturesContracts(ib)
contract = contractDict["MES"]

trades = 0
positions = ibc.GetPositionsOri()  # A list of positions, according to IB

for position in positions:
    if (
        position.contract == contract and
        position.position > 0 and 
        position.contract.right == ''
    ): trades += 1
    print(position)
print(trades)