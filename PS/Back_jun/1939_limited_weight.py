'''
3 3
1 2 2
3 1 3
2 3 2
1 3

6 9
1 2 2
1 3 3
2 4 4
2 3 2
3 4 6
3 5 4
4 5 5
4 6 4
5 6 1
1 6

2 5
1 2 1
1 2 2
1 2 3
1 2 4
1 2 5
1 2


'''
from collections import deque

def bfs(st,mid):

    q = deque([st])
    visited[st] = 1
    while q:
        st = q.popleft()
        if st == island2:
            return True

        for g,gc in graph[st]:
            if visited[g]==0 and mid<=gc:
                q.append(g)
                visited[g]=1

    return False

n,m = map(int,input().split())
graph = [[] for _ in range(n+1)]
for _ in range(m):
    s,f,c = map(int,input().split())
    graph[s].append((f,c))
    graph[f].append((s,c))

island1,island2 = map(int,input().split())
for g in graph:
    g.sort(key=lambda x: x[1], reverse=True)

dy = [-1,0,1,0]
dx = [0,1,0,-1]
start, end = 1,1000000000

while start<=end:
    visited = [0]*(n+1)
    mid = (start+end)//2
    if bfs(island1,mid):
        start = mid+1
    else:
        end = mid-1
print(end)