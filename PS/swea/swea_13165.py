'''
3

1
2 3
0 1 1
0 2 6
1 2 1

1
4 7
0 1 9
0 2 3
0 3 7
1 4 2
2 3 8
2 4 1
3 4 8

1
4 6
0 1 10
0 2 7
1 4 2
2 3 10
2 4 3
3 4 10

'''
import heapq
from collections import deque
def bfs(st):

    q = deque([(st)])
    v = [0]+[1e9]*(n)
    while q:
        c= q.popleft()
        for e,w in graph[c]:
            if v[e]>v[c]+w:
                v[e]=v[c]+w
                q.append(e)
    return v[-1]


for tc in range(1,int(input())+1):

    n,E = map(int,input().split())

    graph = [[] for _ in range(n+1)]
    for _ in range(E):
        s,e,w = map(int,input().split())
        graph[s].append((e,w))
    mn=bfs(0,n)
    print(f"#{tc} {mn}")
    
