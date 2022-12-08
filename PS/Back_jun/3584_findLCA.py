'''

root node의 특징 : 부모노드가 없다

'''
import sys
sys.setrecursionlimit(int(1e5))
# 깊이, 부모 저장하기
def dfs(st,d):

    visited[st]=1
    depth[st] = d
    for node in tree[st]:
        if visited[node]:
            continue
        parents[node] = st
        dfs(node,d+1)

def lca(a,b):

    # make nodes in the same delpth
    while depth[a]!=depth[b]:
        if depth[a] > depth[b]:
            a = parents[a]
        else:
            b = parents[b]

    # if a,b are same, break
    while a!=b:
        a = parents[a]
        b = parents[b]

    return a

T = int(input())
for _ in range(1,T+1):
    n = int(input())
    tree = [[] for _ in range(n+1)]
    parents = [0]*(n+1)
    visited = [0]*(n+1)
    depth = [0]*(n+1)
    root = 0
    root_set = set()
    for _ in range(n-1):
        s,f = map(int,input().split())
        root_set.add(f)
        tree[s].append(f)
        tree[f].append(s)
    for i in range(1,n+1):
        if i not in root_set:
            root = i
    a,b = map(int,input().split())
    dfs(root,0)
    print(lca(a,b))


