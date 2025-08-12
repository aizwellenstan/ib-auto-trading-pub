import numpy as np

npArr = [['5','2023-01-19'],['5','2023-01-30'],['6','2023-01-19']]
# dateFilter = np.asarray(['2023-01-19'])
# npArr[np.in1d(npArr[:,1],dateFilter)]


new_arr = np.array([[14,'m'],[16,'n'],[17,'o'],[21,'p']])
new_arr = np.array(npArr)
dateFilter = np.array(['2023-01-19'])
result = np.in1d(new_arr[:, 1], dateFilter)
z=new_arr[result]
print("Filter 2-dimensional array:",z)