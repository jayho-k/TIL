'''
10
1 2 0 1 3 2 1 5 4 2

시작점 1로 시작을 해서 n번째에 도달한다면 최소 몇번을 움직여야하니??
'''
from collections import deque

def bfs(graph,stp,n):
    visited = [0]*(n+1)
    q = deque([])

    for g in graph[stp]:
        q.append(g)
        visited[g] = 1

    while q:
        tmp = q.popleft()

        for i in graph[tmp]:
            if visited[i] == 0:
                visited[i] = visited[tmp] + 1
                q.append(i)

    return visited

n = int(input())
lst = [0]+list(map(int, input().split()))
graph = deque([[] for _ in range(n+1)])


# graph
for i in range(len(lst)):
    for j in range(1,lst[i]+1):
        if i+j > n:
            break
        graph[i].append(i+j)


v = bfs(graph,1,n)
if n == 1:
    print(0)

else:
    if v[-1] == 0:
        print(-1)
    else:
        print(v[-1])

