'''
3
2 3
0 1 1
0 2 6
1 2 1
4 7
0 1 9
0 2 3
0 3 7
1 4 2
2 3 8
2 4 1
3 4 8
4 6
0 1 10
0 2 7
1 4 2
2 3 10
2 4 3
3 4 10

1
2 3
0 1 1
0 2 6
1 2 1
'''
import heapq

def dsk(st):

    q = []
    heapq.heappush(q,(0,st))
    table[st] = 0

    while q:

        d, nw = heapq.heappop(q)
        if d <= table[nw]:
            
            for dd, nxt in graph[nw]:
                nd = dd + d
                if nd < table[nxt]:
                    table[nxt] = nd
                    heapq.heappush(q,(nd,nxt))


T = int(input())

for tc in range(1,T+1):

    inf = 1e9
    n,m = map(int,input().split())
    
    graph = [[] for _ in range(n+1)]
    table = [inf]*(n+1)

    for _ in range(m):
        s,g,c = map(int,input().split())
        graph[s].append((c,g))

    dsk(0)

    print(f'#{tc} {table[-1]}')
