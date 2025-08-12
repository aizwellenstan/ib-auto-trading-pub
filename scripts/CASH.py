import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__))
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.fourBarTP import FourBarTP
from modules.strategy.vsa import NoSupplyBar
from modules.strategy.trend import UpTrend
from modules.strategy.donchainChannel import DcBreakOut
from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
from modules.strategy.fvg import Fvg
from modules.strategy.combine import Combine
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail, ExecTrailMOC
from modules.trade.utils import GetVol
from ib_insync import Stock, CFD
import pandas as pd
from modules.strategy.threeBarPlay import ThreeBarPlay
from modules.strategy.irb import Irb
from config import load_credentials
ACCOUNT = load_credentials('stockAccount')

ibc = ibc.Ib()
ib = ibc.GetIB(1)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(avalible_cash)