import pandas as pd
import os
import csv

def DumpCsv(path, list):
    df = pd.DataFrame(list, columns = ['Symbol'])
    df.to_csv(path)

def DumpDict(dataDict, colName, path):
    df = pd.DataFrame()
    df['Symbol'] = dataDict.keys()
    df[colName] = dataDict.values()
    df.to_csv(path)

def LoadCsv(path):
    symbolList = []
    if os.path.exists(path):
        df = pd.read_csv(path)
        symbolList = list(df.Symbol.values)
    return symbolList

def LoadDict(path, colName):
    dataDict = {}
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df[['Symbol', colName]]
        df = df.astype({'Symbol':'string'})
        dataDict = df.set_index('Symbol')[colName].to_dict()
    newDict = {}
    for k, v in dataDict.items():
        newDict[k] = v
    return newDict

def load_csv_to_dict(filename):
    result_dict = {}
    with open(filename, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            symbol = row['Symbol']
            del row['Symbol']
            result_dict[symbol] = list(row.values())
    return result_dict

def dump_result_list_to_csv(result_list, filename, header):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        for r in result_list:
            writer.writerow(r)

def load_csv_rows(file_path):
    rows = []
    header = False
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if not header:
                header = True
                continue
            rows.append(row)
    return rows

def dump_result_list_to_csv_utf8(result_list, filename, header):
    with open(filename, mode='w', newline='', encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        for r in result_list:
            writer.writerow(r)
