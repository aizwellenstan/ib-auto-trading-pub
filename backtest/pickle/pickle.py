import pickle
import gc

output = open("./pro/compressed/hisBarsStocksD1arr.p", "rb")
gc.disable()
hisBarsStocksD1arr = pickle.load(output)
output.close()
gc.enable()
print("load hisBarsStocksD1arr finished")