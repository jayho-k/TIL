'''
3
5 2 3 1 1
10 2 1 3 2 2 5 4 2 1
10 1 1 2 1 2 2 1 2 1

'''
from collections import deque

def bfs(st):

    q = deque([st])
    visited[st] = 1
    
    while q:
        t = q.popleft()
        for i in graph[t]:
            
            if 0 not in visited:
                return

            if visited[i] == 0:
                visited[i] = visited[t] + 1
                q.append(i)


T = int(input())
for tc in range(1,T+1):

    n,*cha = list(map(int, input().split()))

    graph = [[] for _ in range(n)]
    visited = [0]*n


    for i in range(len(cha)):
        for j in range(1,cha[i]+1):
            if i+j > n:
                break
            graph[i].append(i+j)


    # print(graph)
    bfs(0)
    # print(visited)

    print(f'#{tc} {visited[-1]-2}')