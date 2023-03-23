'''

2
12 10
1B3B3B81F75E
16 2
F53586D76286B2D8

'''
from collections import deque

def find_mx(lst):
    order_set = set()
    for _ in range(qn):
        lst.rotate()
        for i in range(0,len(lst),qn):
            num = ''
            for j in range(i,qn+i):
                num+=lst[j]
            order_set.add(int(num,16))
    return list(order_set)
                

for tc in range(1,int(input())+1):
    n,k = map(int,input().split())
    lst = deque(list(input()))
    qn = len(lst)//4
    order_lst = find_mx(lst)
    order_lst.sort(reverse=True)
    print(f"#{tc} {order_lst[k-1]}")

