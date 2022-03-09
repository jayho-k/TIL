'''
문제
루트 없는 트리가 주어진다. 이때, 트리의 루트를 1이라고 정했을 때,
각 노드의 부모를 구하는 프로그램을 작성하시오.

7
1 6
6 3
3 5
4 1
2 4
4 7

'''
import sys
sys.setrecursionlimit(10**6)

def dfs(st):
    visited[st] = 1
    for i in graph[st]:
        if not visited[i]:
            ans[i] = st
            dfs(i)
    return

n = int(input())
graph = [[] for _ in range(n+1)]
visited = [0] *(n+1)
ans = [0]*(n+1)

for _ in range(n-1):
    s,g = map(int, input().split())
    graph[s].append(g)
    graph[g].append(s)

dfs(1)

for a in ans[2:]:
    print(a)