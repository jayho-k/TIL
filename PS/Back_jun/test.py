'''
일꾼들이 작업을 한다 일꾼들마다 일의 효율이 다름 어떻게 배분해주면 가장 적은 시간안에 끝낼까

입력
첫줄에는 일꾼의 수 N과 일의양 K가 공백을 기준으로 주어진다
둘째줄부터는 일꾼이 한번 작업하는데 걸리는 시간, 작업하는 일의 양을 기준으로 주어진다

출력
일을 끝낼 수 있는 가장 적은 시간을 정수로 표현해라

2 50
1 10
3 15

4 70
3 10
5 14
6 17
10 100

6 1000
6 99
8 70
20 200
22 222
23 289
40 300
'''
from itertools import permutations, combinations

n, k = map(int,input().split())
worker = [0]

for i in range(n):
    time, work = map(int,input().split())
    worker.append((time,work))

lst = list(range(1,n+1))

for i in range(1,n+1):
    com_lsts = list(map(list,combinations(lst,i)))
    for com_lst in com_lsts:

        total_time = 0
        t = 0
        k_work = 0
        while t<=k:
            for com in com_lst:
                time, work = com
                if t%time == 0:
                    




        






    

