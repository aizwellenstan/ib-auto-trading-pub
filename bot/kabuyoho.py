rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.kabuyoho import GetSmillarCompany
import pandas as pd
from modules.aiztradingview import GetCloseJP
import csv

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'SimilarCompany1', 'SimilarCompany2', 'SimilarCompany3'])
        for symbol, c1, c2, c3 in result_list:
            writer.writerow([symbol, c1, c2, c3])

def main():
    from modules.csvDump import load_csv_to_dict

    csvPath = f"{rootPath}/data/SimilarCompanyJP.csv"
    similarCompanyDict = load_csv_to_dict(csvPath)
    length = len(similarCompanyDict)
    
    closeDict = GetCloseJP()
    res = []

    # print("9942" in closeDict)
    for symbol, close in closeDict.items():
        if symbol in similarCompanyDict:
            similarCompany = similarCompanyDict[symbol]
        else:
            similarCompany = GetSmillarCompany(symbol)
            if len(similarCompany) < 1: continue
        similarCompanyList = [symbol]
        for t in similarCompany:
            similarCompanyList.append(t)
        res.append(similarCompanyList)
    # print(res)
    if len(res) > length:
        dump_result_list_to_csv(res, csvPath)


if __name__ == '__main__':
    main()



