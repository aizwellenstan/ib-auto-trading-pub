import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import polars as pl
import pandas as pd
import os
from sqlalchemy import create_engine
engine = create_engine("duckdb:///:memory:")

FOLDER = f"{rootPath}/data/jp"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)
FILE_PATH = f"{FOLDER}/category.parquet"

def SaveCategories(categories):
    if len(categories) < 1: return 0
    df = pl.DataFrame(categories)
    df.columns = ['ticker', 'category']
    print("WRITING", os.path.abspath(FILE_PATH))
    df.write_parquet(FILE_PATH)

def GetCategoriesDict():
    df = pd.read_parquet(FILE_PATH)
    categoriesDict = df.groupby('category')['ticker'].apply(list).to_dict()
    return categoriesDict

def GetCategoryDict():
    df = pd.read_parquet(FILE_PATH)
    categoryDict = df.set_index('ticker')['category'].to_dict()
    return categoryDict

def GetSymbolList():
    df = pl.read_parquet(FILE_PATH)
    return df['ticker'].to_list()

if __name__ == '__main__':
    # GetCategoriesDict()
    # categoryDict = GetCategoryDict()
    # print(categoryDict)
    symbolList = GetSymbolList()
    print(symbolList)