rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.rironkabuka import GetRironFinancial
rironkabuka, shisannkachi, shuueki, score, d, shijou, gyoushu, haitourimawari, kiborisk = GetRironFinancial("9101")
print(rironkabuka, shisannkachi, shuueki, score, d, shijou, gyoushu, haitourimawari, kiborisk)