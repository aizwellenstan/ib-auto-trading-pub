rootPath = "..";import sys; sys.path.append(rootPath)
from modules.irbank import GetNisshokin

nisshokin = GetNisshokin("9101")
print(nisshokin)