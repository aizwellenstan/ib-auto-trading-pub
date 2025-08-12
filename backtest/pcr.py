rootPath = "..";import sys;sys.path.append(rootPath)
from modules.cboe import getPutCallRatio

pcr = getPutCallRatio()
print(pcr)