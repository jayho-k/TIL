import heapq
import sys
input = sys.stdin.readline

n = int(input())
a,b,c = map(int,input().split())
m = int(input())
graph = [[] for _ in range(n+1)]

for _ in range(m):
    s,f,c = map(int,input().split())
    graph[s].append((c,f))
    graph[f].append((c,s))


def dsk(st):
    
    # 초기화
    table = [1e9]*(n+1)
    table[st] = 0
    q = []
    heapq.heappush(q,(0,st))
    
    while q:
        d, nw =heapq.heappop(q)
        # table값이 만약 더 작아 ==> 패스
        if d > table[nw]:
            continue
 
        # table값이 더 커 ==> 갱신
        for dd, nxt in graph[nw]:
            nd = d + dd

            if table[nxt] > nd:
                table[nxt] = nd
                heapq.heappush(q,(nd, nxt))

    return table


table1 = dsk(a)
table2 = dsk(b)
table3 = dsk(c)

mx = 0
ans = 0
for i in range(1,n+1):
   
    mn = min(table1[i],table2[i],table3[i])
    if mx < mn:
        mx = mn
        ans = i

print(ans)






