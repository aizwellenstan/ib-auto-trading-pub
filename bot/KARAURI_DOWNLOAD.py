import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.karauri import GetSokuhou
from modules.dataHandler.sokuhou import SaveSokuhou

npArr = GetSokuhou('6315', d='2020-01-01')
print(npArr)