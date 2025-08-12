import pandas as pd

def GetBeta(symbol_a,symbol_b):
    column = symbol_a.columns[0]
    beta = symbol_a[column].mean() / symbol_b[column].mean()

    return beta