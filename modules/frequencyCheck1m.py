rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.ib_data import Get1mData

def FrequencyCheck1m(symbol):
    df = Get1mData(symbol,1)
    df = df.drop_duplicates(subset=["open","close"],keep=False)
    if len(df) < 13: return False
    return True

if __name__ == '__main__':
    res = FrequencyCheck1m('HIVE')
    print(res)