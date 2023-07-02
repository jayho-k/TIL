"""
5
1000 1 1
1001 2 1
19998 78 2
2667 37 3
2042 55 3
12
add 1402 59 1
recommend 1 1
recommend2 1
recommend3 1 50
recommend3 -1 50
solved 1000
solved 2667
recommend 2 1
recommend 1 -1
recommend2 -1
solved 1001
recommend 1 -1
"""

import sys
import heapq
from collections import defaultdict


# setting
rec1 = {}
rec2_h = []
rec2_e = []
rec3 = {}
solved = defaultdict(set)
p2l = {}
p_dic = {}

for i in range(1,101):
    rec1[i]=[]
    rec1[-i]=[]
    rec3[i]=[]
    rec3[-i]=[]


# main
input = sys.stdin.readline
n = int(input())

for _ in range(n):
    p,l,g = map(int,input().split())
    p2l[p]=l


# play
m = int(input())
for _ in range(m):
    
    o,*con = input().split()
    
    if o=='recommend':
        g,x = map(int,con)
        if x==1:
            # slove에 있는 것 pop
                      


            pass

        elif x==-1:
            pass



    elif o=='recommend2':
        pass

    elif o=='recommend3':
        pass

    elif o=='add':
        p,l,g = map(int,con)

        # rec1
        heapq.heappush(rec1[g],(-l,-p))
        heapq.heappush(rec1[-g],(l,p))

        # rec2
        heapq.heappush(rec2_h,(-l,-p))
        heapq.heappush(rec2_e,(l,p))

        # rec3
        for a in range(l,101):
            heapq.heappush(rec3[a],(-l,-p))
            heapq.heappush(rec3[-a],(l,p))

        # remove
        # 같은 번호 + 같은 난이도가 있다면 remove
        if p in solved and l in solved[p]:
            solved[p].remove(l)


    elif o=='solved':
        p = int(con[0])
        l = p2l[p]
        solved[p].add(l)


