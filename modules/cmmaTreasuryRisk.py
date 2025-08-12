rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.cmma import Cmma
from modules.data import GetDataWithVolumeDate
import numpy as np

def GetTreasuryRisk():
    scheNpArr = GetDataWithVolumeDate("SCHE", "2018-01-01")
    tnxNpArr = GetDataWithVolumeDate("^TNX", "2018-01-01")

    scheCmma = Cmma(scheNpArr)
    tnxNpArr = Cmma(tnxNpArr)
    return np.array(scheCmma/tnxNpArr)
