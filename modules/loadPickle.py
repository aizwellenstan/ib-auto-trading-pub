import pickle

def LoadPickle(picklePath):
    output = open(picklePath, "rb")
    res = pickle.load(output)
    output.close()
    return res