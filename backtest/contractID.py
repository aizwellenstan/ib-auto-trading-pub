rootPath = ".."
import sys
sys.path.append(rootPath)
import modules.ib as ibc
from modules.ibWebPortal import GetMarketData, GetContractDetails

ibc = ibc.Ib()
ib = ibc.GetIB(10)

symbol = "9101"
contract = ibc.GetStockContractJP(symbol)
print(contract.conId)

GetMarketData(["3906045"])
# GetContractDetails("3906045")


# http://localhost:5000/v1/api/iserver/marketdata/snapshot