'''


'''
from multiprocessing import Pool
import multiprocessing as mp
import time
import os

def callback(result):
    print('result : ',result)

def f(n):

    if n <= 5:
        return False

    else:
        return True

if __name__ == "__main__":
    
    with Pool(os.cpu_count()) as p:
        result = p.map_async(f, list(range(1,13)),callback=callback)
        result.wait()
        # print(result.get())














