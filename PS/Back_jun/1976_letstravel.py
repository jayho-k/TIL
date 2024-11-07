"""
3
3
0 1 0
1 0 1
0 1 0
1 2 3
"""
from pprint import pprint
from collections import deque

def bfs(s):

    q = deque()    
    visited = set()

    q.append(s)
    visited.add(s)

    while q:
        t = q.popleft()
        for g in graph[t]:
            if g not in visited:
                q.append(g)
                visited.add(g)
    return visited

def makeAnd():
    for p in planList:
        p-=1
        if p not in visSet:
            return "NO"
    return "YES"


n = int(input())
m = int(input())

graph = [set() for _ in range(n)]

for i in range(n):
    lst = list(map(int,input().split()))
    for j in range(len(lst)):
        if lst[j] == 1:
            graph[j].add(i)
            graph[i].add(j)

planList = list(map(int, input().split()))
visSet = bfs(planList[0]-1)
print(makeAnd())
