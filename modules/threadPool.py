from concurrent.futures import ThreadPoolExecutor, as_completed

def HandleFunc(func, symbol):
    return [symbol, func(symbol)]

def ThreadPool(excuteList, func):
    results = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(HandleFunc, func, symbol) for symbol in excuteList]
            for future in as_completed(futures):
                result = future.result()
                try:
                    if len(result[1]) < 1: continue
                    results[result[0]] = result[1]
                except: continue
    return results