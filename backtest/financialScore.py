rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.rironkabuka import GetRironFinancial

riron, score, financialScore = GetRironFinancial("3923")
print(riron, score, financialScore)