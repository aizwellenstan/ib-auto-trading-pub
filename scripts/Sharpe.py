# import sys
# sys.path.append('.')

# from modules.portfolio import GetSharpeSortino
# from modules.aiztradingview import GetDividends
# divs = GetDividends()

# def CheckSharpeSortino(npArr):
#     if npArr[0][0] > npArr[1][0] or npArr[0][1] > npArr[1][1]:
#         return True
#     return False

# sharpeDict = {}
# sortinoDict = {}

# for symbol in divs:
#     npArr = GetSharpeSortino(symbol)
#     if len(npArr) < 2: continue
#     if CheckSharpeSortino(npArr):
#         sharpeDict[symbol] = npArr[0][0]
#         sortinoDict[symbol] = npArr[0][1]
#         print(symbol)

# sharpeDict = dict(sorted(sharpeDict.items(), key=lambda item: item[1], reverse=True))
# sortinoDict = dict(sorted(sortinoDict.items(), key=lambda item: item[1], reverse=True))

# print(sharpeDict)
# print(sortinoDict)