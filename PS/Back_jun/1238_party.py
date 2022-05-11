def dsk(st,table):

    # 초기화
    q = []
    heapq.heappush(q,(0,st))
    table[st] = 0
    
    while q:

        d, nw = heapq.heappop(q)
        if d <= table[nw]:
            for dd, nxt in graph[nw]:
                nd = d + dd
                if nd < table[nxt]:
                    table[nxt] = nd
                    heapq.heappush(q,(nd,nxt))


import sys
import heapq
input = sys.stdin.readline
n, m, x = map(int,input().split())
graph = [[] for _ in range(n+1)]



for _ in range(m):
    s,f,c = map(int,input().split())
    graph[s].append((c,f))


table = [1e9]*(n+1)
dsk(x,table)


mx = 0
for i in range(1,n+1):
    table1 = [1e9]*(n+1)
    if i == x:
        continue
    dsk(i, table1)
    mx = max(mx, table1[x]+table[i])

print(mx)