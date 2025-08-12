import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import modules.ib as ibc
from modules.trade.options import CheckCloseNaketPuts

ibc = ibc.Ib()
ib = ibc.GetIB(4)

def main():
    while(ib.sleep(60)):
        CheckCloseNaketPuts(ibc, "SPX")
        
if __name__ == '__main__':
    main()