'''
5 4
3 1
3 2
4 3
5 3


'''

def bfs(start):

    q = deque([start])
    visited[start] = 1
    cnt = 1
    while q:
        num = q.popleft()

        for g in graph[num]:
            if visited[g] ==0:
                q.append(g)
                visited[g] = 1
                cnt += 1
    return cnt


import sys
from collections import deque

input = sys.stdin.readline
n,m = map(int,input().split())
graph = [[] for _ in range(n+1)]

mx = 0

for _ in range(m):
    s,f = map(int,input().split())
    # graph[s].append(f)
    graph[f].append(s)

lst = [0]
mx = 0
for i in range(1,n+1):
    visited = [0]*(n+1)
    cnt = bfs(i)
    mx = max(mx, cnt)
    lst.append(cnt)

ans_lst = []
for j in range(len(lst)):
    if lst[j] == mx:
        ans_lst.append(j)

print(*ans_lst)