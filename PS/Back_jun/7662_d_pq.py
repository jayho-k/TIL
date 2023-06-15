"""
2
7
I 16
I -5643
D -1
D 1
D 1
I 123
D -1
9
I -45
I 653
D 1
I -642
I 45
I 97
D 1
D -1
I 333


1
5
I 1
I 2
I 3
D 1
D -1


"""
import heapq
from collections import defaultdict
for _ in range(int(input())):
    max_q = []
    min_q = []
    set_q = defaultdict(int)

    for _ in range(int(input())):
        op,num = input().split()
        if op=="I":
            heapq.heappush(max_q,-int(num))
            heapq.heappush(min_q,int(num))
            set_q[int(num)] += 1        

        else:
            if int(num)==1:
                while max_q and set_q[-max_q[0]]<=0:
                    heapq.heappop(max_q)
                
                if max_q:
                    set_q[-heapq.heappop(max_q)]-=1
                    

            else:
                while min_q and set_q[min_q[0]]<=0:
                    heapq.heappop(min_q)
            
                if min_q:
                    set_q[heapq.heappop(min_q)] -= 1
                    

    mn = 1e10
    mx = -1e10
    print(mn)
    for i in set_q:
        if set_q[i]>0:
            mn = min(mn,i)
            mx = max(mx,i)
    # print(min_q)
    # print(max_q)
    # print(set_q)
    if mx==-1e9 and mn==1e9:
        print("EMPTY")
    else:
        print(mx,mn)

