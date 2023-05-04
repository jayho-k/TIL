from multiprocessing import Pool
import multiprocessing as mp
import time
import os

 

def func(num):
    process = mp.current_process()
    print("Start | ","name : ",process.name, "pid : ",process.pid,"num : ",num)
    time.sleep(1)
    print("End   | ","name : ",process.name, "pid : ",process.pid,"num : ",num)
    return num*num



if __name__ == '__main__':

    # Pool로 시작하고 자동으로 꺼지게 된다.
    start = time.time()
    with Pool(os.cpu_count()) as p:
        ret = p.map_async(func,list(range(1,13)))
        print(ret.get())
        delta_t = time.time() - start
    print(delta_t)