'''
Lowest Common Ancestor
'''

import sys
sys.setrecursionlimit(int(1e5))
n = int(input())

parent = [0]*(n+1) # 부모 노드 정보 저장
depth = [0]*(n+1) # 각노드까지의 깊이 저장
visited = [0]*(n+1) # visited
graph = [[] for _ in range(n+1)]

for _ in range(n-1):
    a,b = map(int,input().split())
    graph[a].append(b)
    graph[b].append(a)

# parent값, depth체크하기
def dfs(st,d):
    visited[st] = 1 # 방문
    depth[st] = d # 현재 노드의 깊이가 몇인지 체크
    for node in graph[st]:
        if visited[node]: # 방문한 것이라면 패스
            continue
        parent[node] = st # 이 노드의 parent는 st이다 라는 뜻
        dfs(node, d+1)

# 공통 조상 찾기
def lca(a,b):
    # 먼저 깊이가 동일하도록 만들기
    # a와 b의 깊이가 동일해지게 된다
    while depth[a]!=depth[b]: # a와 b의 깊이가 같아지면 break
        # a의 깊이가 더 깊으면 a를 한칸 올려라
        if depth[a] > depth[b]: 
            a = parent[a] 
        else:
            b = parent[b]
    
    
    while a != b: # a와 b의 값이 같아지면 break
        a = parent[a]
        b = parent[b]
    return a 

dfs(1,0)

m = int(input())

for i in range(m):
    a,b = map(int,input().split())
    print((lca(a,b)))
