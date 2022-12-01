'''


'''


import heapq
import sys

n = int(input())
lst = []
for _ in range(n):
    just = int(sys.stdin.readline().rstrip())
    if just == 0:
        if not lst:
            print(0)
        else:
            a = heapq.heappop(lst)
            print(a[1])
    else:
        heapq.heappush(lst,(abs(just),just))




