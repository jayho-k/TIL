'''
13
0
1
2
0
0
3
2
1
0
0
0
0
0
'''
import heapq
import sys
input = sys.stdin.readline
n = int(input())
lst = []
for _ in range(n):
    x = int(input())
    if x == 0:
        if lst == []:
            print(0)
        else:
            print(heapq.heappop(lst))
        
    else:
        heapq.heappush(lst,x)
        