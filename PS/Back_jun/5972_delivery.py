'''


'''
import heapq
import sys

def dst(st):

    q = []
    heapq.heappush(q,(0,st))
    table[st] = 0

    while q:
        d, nw= heapq.heappop(q)
        
        # table에 있는 값이 더 크거나 같아? => 그럼 갱신
        if table[nw] >= d:
            
            for dd, nxt in graph[nw]:
                nd = d + dd

                if table[nxt] > nd:
                    table[nxt] = nd
                    heapq.heappush(q,(nd,nxt))


input = sys.stdin.readline
inf = 1e9
n, m = map(int,input().split())
graph = [[] for _ in range(n+1)]
table = [inf]*(n+1)

for _ in range(m):
    s,f,c = map(int,input().split())
    graph[s].append((c,f))
    graph[f].append((c,s))

dst(1)

print(table[n])