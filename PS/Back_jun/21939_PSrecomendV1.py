'''
5
1000 1
1001 2
19998 78
2667 37
2042 55
8
add 1402 59
recommend 1
solved 1000
solved 19998
recommend 1
recommend -1
solved 1001
recommend -1
'''
import heapq
from collections import defaultdict

n = int(input())
big = []
small = []
num_dic = defaultdict(list)
for _ in range(n):
    pnum,lnum = map(int,input().split())
    heapq.heappush(small,lnum)
    heapq.heappush(big,-lnum)
    num_dic[lnum].append(pnum)

m = int(input())
for _ in range(m):
    order,*tmp = input().split()

print(num_dic)





