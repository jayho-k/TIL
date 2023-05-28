import time
import threading
import threading_IO # 뭔지 알아보기

n = 5

def for_print():
    print("speeping 1s")
    time.sleep(1)
    print("done")


def with_thread():
    start = time.time()
    threads = []

    # thread를 여러개를 초기화한다..
    # 그리고 각각의 쓰레드를 리스트에 담아준다.
    for _ in range(n):
        t = threading.Thread(target=for_print)
        t.start()
        threads.append(t)

    # 모든 쓰레드가 실행이 완료된 후 다음 코드를 실행시키기 위해 join을 해준다
    for i in range(n):
        threads[i].join()
    print(time.time()-start)

def without_thread():
    
    start = time.time()
    for _ in range(n):
        for_print()
    print(time.time()-start)



if __name__ == '__main__':
    order = input()
    if order == 'thread':
        with_thread()
        
    else:
        without_thread()