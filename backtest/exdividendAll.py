rootPath = ".."
import sys
sys.path.append(rootPath)
import modules.exdividend as exdividend

exdividendTime = exdividend.GetExDividendTime("AAPL","USD")
print(exdividendTime)