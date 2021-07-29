from Precompute import Precompute
from naive import Naive
import time
import os, psutil
from operator import itemgetter

dataset = 'dataset/independent/d/random_50000_3d_ind.csv'
# tic = time.perf_counter()
# naive = Naive(dataset)
# toc = time.perf_counter()
# print('Time Naive: '+str(toc-tic)+' s')

grid_size = 10
tic = time.perf_counter()
pre = Precompute(grid_size, dataset)
print('Precomputing Memory usage: '+str(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)+' mb')
toc = time.perf_counter()
print('Time Grid (size = '+str(grid_size)+'): '+str(toc-tic)+' s')

while 1 :
  time_start = int(input('masukkan time awal : '))
  if time_start == -1:
    break
  time_end = int(input('masukkan time akhir : '))
  thres = int(input('masukkan threshold (%) : '))

  thres = thres/100

  result1 = pre.get_durable_data(time_start, time_end, thres)
  result1 = sorted(result1, key=itemgetter('id')) 

  # result2 = naive.get_durable_data(time_start, time_end, thres)
  # result2 = sorted(result2, key=itemgetter('id')) 

  # tic = time.perf_counter()
  # for event in result2:
  #     print (event)
  # toc = time.perf_counter()
  # print('Time query: '+str(toc-tic)+' s')
  # print('Memory usage: '+str(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)+' mb')

  # print('=============')

  tic = time.perf_counter()
  for event in result1:
      print (event)
  toc = time.perf_counter()
  print('Time query: '+str(toc-tic)+' s')
  print('Memory usage: '+str(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)+' mb')