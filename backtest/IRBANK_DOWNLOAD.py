rootPath = "..";import sys;sys.path.append(rootPath)
from modules.irbank import GetChart, GetEmployee
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from numba import njit
import numpy as np

def HandleGetEmployee(symbol):
    employee = GetEmployee(symbol)
    return [symbol, employee]

def HandleGetChart(symbol):
    chart = GetChart(symbol)
    return [symbol, chart]

def main():
    employeePath = f"{rootPath}/backtest/pickle/pro/compressed/employee.p"

    closeDictJP = GetCloseJP()
    symbolList = list(closeDictJP.keys())

    employeeDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetEmployee, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            employee= result[1]
            if len(employee) < 1: continue
            employeeDict[symbol] = employee
    pickle.dump(employeeDict, open(employeePath, "wb"))
    print("pickle dump finished")

if __name__ == '__main__':
    main()