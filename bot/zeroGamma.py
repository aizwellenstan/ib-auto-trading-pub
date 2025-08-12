import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.zero_gamma import GetZeroGamma
from modules.discord import Alert

def AlertZeroGammaStrike(symbol):
    zeroGammaStrike = GetZeroGamma(symbol)
    message = f"{symbol} ZeroGammaStrike {zeroGammaStrike}"
    Alert(message)

AlertZeroGammaStrike('SPY')
AlertZeroGammaStrike('QQQ')
AlertZeroGammaStrike('DIA')
AlertZeroGammaStrike('SPX')
