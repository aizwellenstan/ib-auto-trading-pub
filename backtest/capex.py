import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.yfquery import GetCapex

income = GetCapex("AAPL")
# print(income)

import json
with open("capex.json", "w") as outfile: 
    json.dump(income, outfile)
