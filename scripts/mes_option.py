import json
import redis
from modules.discord import Alert
import modules.ib as ibc
from config import load_credentials
from modules.trade.futures import GetFuturesContracts, ExecBracket
from ib_insync import Contract, Option, ComboLeg

ACCOUNT = load_credentials('futuresAccount')
ibc = ibc.Ib()
ib = ibc.GetIB(1)
contractDict = GetFuturesContracts(ib)
contract = contractDict["MES"]
# print(contract.secType)
# chains = ibc.GetOptionChains(contract)
# print(chains)
def GetOptionContract(symbol, expir, strike, optType):
    option_contract = Option(symbol, expir, strike, optType, 'SMART', tradingClass=symbol)
    return option_contract

option_c_long_call = GetOptionContract("MES", "20250509", 5700, 'C')
option_c_short_call = GetOptionContract("MES", "20250509", 5710, 'C')
print(option_contract)


leg1 = ComboLeg()
leg1.conId = option_c_long_call.conId
leg1.ratio = 1
leg1.action = "BUY"
leg1.exchange = "CME"

leg2 = ComboLeg()
leg2.conId = option_c_short_call.conId
leg2.ratio = 1
leg2.action = "SELL"
leg2.exchange = "CME"

contract.comboLegs = []
contract.comboLegs.append(leg1)
contract.comboLegs.append(leg2)

spread_order = Order()
spread_order.action = 'BUY'
spread_order.orderType = "MKT"
spread_order.totalQuantity = 1
spread_order.smartComboRoutingParams = []
spread_order.smartComboRoutingParams.append(TagValue('NonGuaranteed', '1'))
ib.placeOrder(contract, spread_order)