import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from modules.dataHandler.category import GetSymbolList
from modules.karauri import GetSokuhou
from modules.dataHandler.sokuhou import SaveSokuhou

def generate_date_range(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date.strftime('%Y-%m-%d')
        current_date += timedelta(days=1)

def HandleGetSokuhou(symbol, dateList):
    for da in dateList:
        sokuhou = GetSokuhou(symbol, da)
        SaveSokuhou(symbol, sokuhou)
    return [symbol, sokuhou]

def main():
    symbolList = GetSymbolList()

    start_date = datetime(2020, 3, 1)
    end_date = datetime.now()

    date_list = list(generate_date_range(start_date, end_date))

    download = []
    for i in range(0, len(date_list), 60):
        download.append(date_list[i])
    download.append(date_list[-1])

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetSokuhou, symbol, download) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()


if __name__ == '__main__':
    main()